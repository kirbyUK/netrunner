import argparse
from datetime import date
import json
import functools
from math import floor
from multiprocessing import Pool
from netrunner.netrunnerdb.card import Card
from netrunner.netrunnerdb.decklist import Decklist
from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning
from netrunner.alwaysberunning.event import Event
from pathlib import Path
import re
import sys
import traceback
from typing import Any, Dict, List, Optional, Set, Tuple

from sklearn.cluster import DBSCAN


class CacheTournament:
    """A cut-down tournament object that can be cached."""

    def __init__(self, path: Path) -> None:
        with open(path, "r", encoding="utf8") as f:
            d = json.load(f)
        self._id = d["id"]
        self._name = d["name"]
        self._decks = { int(placement): ids for placement, ids in d["decks"].items() }

    @property
    def id(self) -> int:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def decks(self) -> Dict[int, List[Optional[str]]]:
        return self._decks


class CacheDecklist:
    """A cut-down decklist object that can be cached."""

    def __init__(self, decklist: Optional[Decklist] = None, path: Optional[Path] = None) -> None:
        if decklist is not None:
            self._id = decklist.id
            self._name = decklist.name
            self._cards = decklist.cards
            self._url = f"https://netrunnerdb.com/en/decklist/{decklist.uuid}"
        elif path is not None:
            with open(path, "r", encoding="utf8") as f:
                d = json.load(f)
            self._id = d["id"]
            self._name = d["name"]
            self._cards = { Card(id): quantity for id, quantity in d["cards"].items() }
            self._url = d["url"]
        else:
            raise Exception
        
    def __eq__(self, other: Any) -> bool:
        return type(other) is CacheDecklist and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
        
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def cards(self) -> Dict[Card, int]:
        return self._cards
    
    @property
    def url(self) -> str:
        return self._url


class Cache:
    """Caching for tournaments and decklists."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.decklist_cache_dir = self.cache_dir.joinpath("decklists")
        self.decklist_cache_dir.mkdir(parents=True, exist_ok=True)
        self.tournament_cache_dir = self.cache_dir.joinpath("tournaments")
        self.tournament_cache_dir.mkdir(exist_ok=True)

    def cache_decklist(self, decklist: Decklist):
        with open(self.decklist_cache_dir.joinpath(f"{decklist.id}.json"), "w", encoding="utf8") as f:
            json.dump({
                "id": decklist.id,
                "name": decklist.name,
                "cards": { card.code: quantity for card, quantity in decklist.cards.items() },
                "url": f"https://netrunnerdb.com/en/decklist/{decklist.uuid}",
            }, f, indent=4)

    def cache_tournament(self, tournament: Event, decks: Dict[int, List[Optional[int]]]):
        with open(self.tournament_cache_dir.joinpath(f"{str(tournament.id)}.json"), "w", encoding="utf8") as f:
            json.dump({
                "id": tournament.id,
                "name": tournament.title,
                "decks": { placement: [
                    id if id is not None else None
                    for id in deck_ids ]
                for placement, deck_ids in decks.items() }
            }, f, indent=4)

    def get_decklist(self, id: int) -> Optional[CacheDecklist]:
        path = self.decklist_cache_dir.joinpath(f"{id}.json")
        if path.is_file():
            return CacheDecklist(path=path)
        else:
            return None

    def get_tournament(self, id: int) -> Optional[CacheTournament]:
        path = self.tournament_cache_dir.joinpath(f"{id}.json")
        if path.is_file():
            return CacheTournament(path=path)
        else:
            return None


def main():
    output_file, start_date, end_date, tournament_format, top_percentage, eps, min_samples = args()
    abr = AlwaysBeRunning()

    print(f"[+] Getting completed {tournament_format} events from {start_date.isoformat()} to {end_date.isoformat()}")

    # Get all events that match our filters.
    events = list(
        filter(
            lambda event:
                (event.format or "") == tournament_format and
                (start_date <= (event.date or date(2000, 1, 1)) <= end_date),
            all_events(abr)
        )
    )

    print(f"[+] Getting decklists for {len(events)} tournaments")

    cache = Cache(Path("cluster-cache"))
    cache_events(events, cache)

    # Get all decklists from these events that match our filters, split out over
    # a multiprocessing pool to get it done quicker.
    decklist_getter = functools.partial(decklists_from_event, top_percentage, cache)
    with Pool() as pool:
        decklists = [x for xs in pool.map(decklist_getter, [cache.get_tournament(event.id) for event in events]) for x in xs]
    """
    decklists = [decklists_from_event(top_percentage, cache, tournament) for tournament in [cache.get_tournament(event.id) for event in events]]
    """

    # Split our decklist tuples into corp and runner sets.
    corp_decks = set([decklist[0] for decklist in decklists if decklist[0] is not None])
    runner_decks = set([decklist[1] for decklist in decklists if decklist[1] is not None])
    
    # Cluster the decklists.
    print(f"[+] Clustering {len(corp_decks)} corp decks")
    clustered_corp_decks = cluster_decklists(corp_decks, eps, min_samples)

    print(f"[+] Clustering {len(runner_decks)} runner decks")
    clustered_runner_decks = cluster_decklists(runner_decks, eps, min_samples)

    # Write the markdown.
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"## Corp\n")
        for label, decks in clustered_corp_decks.items():
            f.write(f"\n### {label}\n\n")
            for deck in decks:
                f.write(f"* [{deck.name}]({deck.url})\n")

            f.write(f"\n#### Most Common Cards\n\n")
            for card, quantity in most_common_cards(decks):
                f.write(f"* [{card.title}](https://netrunnerdb.com/en/card/{card.code}) ({quantity} copies)\n")

        f.write("\n")

        f.write(f"## Runner\n")
        for label, decks in clustered_runner_decks.items():
            f.write(f"\n### {label}\n\n")
            for deck in decks:
                f.write(f"* [{deck.name}]({deck.url})\n")

            f.write(f"\n#### Most Common Cards\n\n")
            for card, quantity in most_common_cards(decks):
                f.write(f"* [{card.title}](https://netrunnerdb.com/en/card/{card.code}) ({quantity} copies)\n")


def args() -> Tuple[str, date, date, str, float, float, int]:
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(
        prog="netrunner-cluster",
        description="DBSCAN Clustering for Netrunner top decks"
    )

    parser.add_argument("--output", "-o", default=f"rwr_{date.today().isoformat()}.md", help="Output filename")
    parser.add_argument("--start-date", default="2024-05-25", help="Start date for completed events (inclusive)")
    parser.add_argument("--end-date", default=date.today().isoformat(), help="End date for completed events (inclusive)")
    parser.add_argument("--format", default="standard", choices=["standard", "startup"], help="The format to get completed decks for")
    parser.add_argument("--percentage", default=30, type=int, help="Percentage of decks to collect from tournaments (0-100)")
    parser.add_argument("--eps", default=7.5, type=float, help="EPS value for DBSSCAN algorithm")
    parser.add_argument("--min-samples", default=3, type=int, help="Minimum number of samples to form a cluster")

    args = parser.parse_args()

    if args.percentage < 0 or args.percentage > 100:
        sys.stderr.write("--percentage arg must be between 0 and 100\n")
        raise Exception

    return (
        args.output,
        date.fromisoformat(args.start_date),
        date.fromisoformat(args.end_date),
        args.format,
        args.percentage / 100,
        args.eps,
        args.min_samples
    )


def cache_events(events: List[Event], cache: Cache):
    for event in events:
        # If we already have a cache entry for this tournament, start with that
        # and merge the two.
        cached_event = cache.get_tournament(event.id)
        if cached_event is not None:
            decks = cached_event.decks
        else:
            decks = {}

        # Get the decklist used for each entry.
        for entry in event.entries():
            if entry.corp_deck_url is not None:
                corp_deck_id = get_decklist_id(entry.corp_deck_url)
            else:
                corp_deck_id = None

            if entry.runner_deck_url is not None:
                runner_deck_id = get_decklist_id(entry.runner_deck_url)
            else:
                runner_deck_id = None

            if entry.rank_swiss is not None:
                if entry.rank_swiss not in decks:
                    decks[entry.rank_swiss] = [None, None]

                if corp_deck_id is not None:
                    decks[entry.rank_swiss][0] = corp_deck_id

                if runner_deck_id is not None:
                    decks[entry.rank_swiss][1] = runner_deck_id

        # Cache the event.
        cache.cache_tournament(event, decks)


def decklists_from_event(top_percentage: float, cache: Cache, tournament: CacheTournament) -> List[Tuple[Optional[CacheDecklist], Optional[CacheDecklist]]]:
    """Get all decklists from an event that fall in the top given percentage."""
    decks = []

    participants = len(tournament.decks)
    try:
        for placement in range(1, floor(participants * top_percentage)):
            deck_ids = tournament.decks[placement]
            corp = None
            runner = None

            if deck_ids[0] is not None:
                corp_cached = cache.get_decklist(deck_ids[0])

                if corp_cached is not None:
                    corp = corp_cached
                else:
                    try:
                        corp_full_list = Decklist(id=deck_ids[0])
                        cache.cache_decklist(corp_full_list)
                        corp = CacheDecklist(decklist=corp_full_list)
                    except:
                        sys.stderr.write(f"failed on {deck_ids[0]}\n")

            if deck_ids[1] is not None:
                runner_cached = cache.get_decklist(deck_ids[1])

                if runner_cached is not None:
                    runner = runner_cached
                else:
                    try:
                        runner_full_list = Decklist(id=deck_ids[1])
                        cache.cache_decklist(runner_full_list)
                        runner = CacheDecklist(runner_full_list)
                    except:
                        sys.stderr.write(f"failed on {deck_ids[1]}\n")
            

            decks.append((corp, runner))
    except Exception:
        sys.stderr.write(f"failed on entries for {tournament.name}:\n")
        traceback.print_exc()

    return decks


def all_events(abr: AlwaysBeRunning) -> Set[Event]:
    """Get all ABR events."""
    all_events: Set[Event] = set()
    offset = 0
    events = abr.results(offset=offset)
    while len(events) >= 500:
        all_events = all_events.union(set(events))
        events = abr.results(offset=offset)
        offset += 500

    return all_events


def get_decklist_id(url: str) -> str:
    m = re.search("decklist/([0-9]+)", url)
    if m is not None:
        id = str(m.group(1))
        return id
    else:
        raise Exception


def cluster_decklists(decks: Set[CacheDecklist], eps: float, min_samples: int) -> Dict[int, List[CacheDecklist]]:
    """Cluster the given decks and return each keyed on its cluster number."""
    cards = all_cards(decks)
    vectored_decklists = [vectorise_decklist(cards, deck) for deck in decks]

    # eps = Maximum distance between the samples to be in the same cluster.
    #       Greater numbers means less correlated decks are grouped together,
    #       smaller numbers starts to remove less related decks as noise.
    #
    # min_samples = Minimum number of items in a cluster. Clusters with too few
    #               items are removed as noise.
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(vectored_decklists)
    labels = list(db.labels_)
    decks_with_labels = list(zip(decks, labels))
    number_of_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    return { label: [ deck for
                      deck, deck_label in decks_with_labels
                      if deck_label == label ]
             for label in range(0, number_of_clusters) }


def all_cards(all_decklists: Set[CacheDecklist]) -> List[Card]:
    """Get all cards from all decklists."""
    return sorted(list(set([card
                            for decklist in all_decklists
                            for card in decklist.cards])),
                  key=lambda card: card.title)


def vectorise_decklist(all_cards: List[Card], decklist: CacheDecklist) -> List[int]:
    """Convert a decklist to a vector."""
    vector = [0] * len(all_cards)
    for card, quantity in decklist.cards.items():
        vector[all_cards.index(card)] = quantity

    return vector


def most_common_cards(decks: List[CacheDecklist], number_of_cards=10) -> List[Tuple[Card, int]]:
    """Get the 20 most common cards from the given list of decks."""
    card_counts: Dict[Card, int] = dict()

    # Count cards across all decks.
    for deck in decks:
        for card, quantity in deck.cards.items():
            if card not in card_counts:
                card_counts[card] = quantity
            else:
                card_counts[card] += quantity

    # Get the top cards.
    n = number_of_cards if len(card_counts) > number_of_cards else len(card_counts) - 1
    return sorted(card_counts.items(), key=lambda x: x[1], reverse=True)[:n]


if __name__ == "__main__":
    main()
