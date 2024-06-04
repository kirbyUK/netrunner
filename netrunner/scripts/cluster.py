import argparse
from datetime import date
import functools
from math import floor
from multiprocessing import Pool
from netrunner.netrunnerdb.card import Card
from netrunner.netrunnerdb.decklist import Decklist
from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning
from netrunner.alwaysberunning.event import Event
import sys
from typing import Dict, List, Optional, Set, Tuple

from sklearn.cluster import DBSCAN


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

    # Get all decklists from these events that match our filters, split out over
    # a multiprocessing pool to get it done quicker.
    decklist_getter = functools.partial(decklists_from_event, top_percentage)
    with Pool() as pool:
        decklists = [x for xs in pool.map(decklist_getter, events) for x in xs]

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
                f.write(f"* [{deck.name}](https://netrunnerdb.com/en/decklist/{deck.uuid})\n")

            f.write(f"\n#### Most Common Cards\n\n")
            for card, quantity in most_common_cards(decks):
                f.write(f"* [{card.title}](https://netrunnerdb.com/en/card/{card.code}) ({quantity} copies)\n")

        f.write("\n")

        f.write(f"## Runner\n")
        for label, decks in clustered_runner_decks.items():
            f.write(f"\n### {label}\n\n")
            for deck in decks:
                f.write(f"* [{deck.name}](https://netrunnerdb.com/en/decklist/{deck.uuid})\n")

            f.write(f"\n#### Most Common Cards\n\n")
            for card, quantity in most_common_cards(decks):
                f.write(f"* [{card.title}](https://netrunnerdb.com/en/card/{card.code}) ({quantity} copies)\n")


def args() -> Tuple[str, date, date, str, float, float, int]:
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(
        prog="cluster",
        description="k-Means Clustering for Netrunner top decks"
    )

    parser.add_argument("--output", "-o", default=f"rwr_{date.today().isoformat()}.md", help="Output filename")
    parser.add_argument("--start-date", default="2024-03-18", help="Start date for completed events (inclusive)")
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


def decklists_from_event(top_percentage: float, tournament: Event) -> List[Tuple[Optional[Decklist], Optional[Decklist]]]:
    """Get all decklists from an event that fall in the top given percentage."""
    decks = []

    try:
        for entry in filter(
            lambda entry: 1 <= (entry.rank_swiss or 0) <= floor(len(tournament.entries()) * top_percentage),
            tournament.entries()
        ):
            corp = None
            runner = None

            if entry.corp_deck_url is not None:
                try:
                    corp = Decklist(url=entry.corp_deck_url)
                except:
                    sys.stderr.write(f"failed on {entry.corp_deck_url}\n")

            if entry.runner_deck_url is not None:
                try:
                    runner = Decklist(url=entry.runner_deck_url)
                except:
                    sys.stderr.write(f"failed on {entry.runner_deck_url}\n")

            decks.append((corp, runner))
    except:
        sys.stderr.write(f"failed on entries for {tournament.title}\n")

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


def cluster_decklists(decks: Set[Decklist], eps: float, min_samples: int) -> Dict[int, List[Decklist]]:
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


def all_cards(all_decklists: Set[Decklist]) -> List[Card]:
    """Get all cards from all decklists."""
    return sorted(list(set([card
                            for decklist in all_decklists
                            for card in decklist.cards])),
                  key=lambda card: card.title)


def vectorise_decklist(all_cards: List[Card], decklist: Decklist) -> List[int]:
    """Convert a decklist to a vector."""
    vector = [0] * len(all_cards)
    for card, quantity in decklist.cards.items():  
        vector[all_cards.index(card)] = quantity

    return vector


def most_common_cards(decks: List[Decklist], number_of_cards=10) -> List[Tuple[Card, int]]:
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
