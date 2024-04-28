from datetime import date
from io import TextIOWrapper
from math import ceil
from multiprocessing import Pool
from netrunner.netrunnerdb.card import Card
from netrunner.netrunnerdb.decklist import Decklist
from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning
from netrunner.alwaysberunning.event import Event
import os
import sys
from typing import List, Optional, Set, Tuple

from sklearn.cluster import KMeans


def main():
    abr = AlwaysBeRunning()

    # Get all events that match our filters.
    events = list(
        filter(
            lambda event:
                (event.format or "") == "standard" and
                (date(2024, 3, 18) <= (event.date or date(2000, 1, 1)) <= date.today()),
            all_events(abr)
        )
    )

    # Get all decklists from these events that match our filters, split out over
    # a multiprocessing pool to get it done quicker.
    with Pool() as pool:
        decklists = [x for xs in pool.map(decklists_from_event, events) for x in xs]

    # Split our decklist tuples into corp and runner sets.
    corp_decks = set([decklist[0] for decklist in decklists if decklist[0] is not None])
    runner_decks = set([decklist[1] for decklist in decklists if decklist[1] is not None])
    
    # Cluster the corp decklists and print the markdown.
    with open(f"rwr_{date.today().isoformat()}.md", "w", encoding="utf-8") as f:
        f.write(f"## Corp\n")
        cluster_decklists(corp_decks, 14, f)
        f.write(os.linesep)

        # Cluster the runner decklists and print the markdown.
        f.write(f"## Runner\n")
        cluster_decklists(runner_decks, 10, f)
        f.write(os.linesep)


def decklists_from_event(tournament: Event) -> List[Tuple[Optional[Decklist], Optional[Decklist]]]:
    """Get all decklists from an event that fall in the top 30%."""
    decks = []

    try:
        print(tournament.title)
    except:
        pass

    try:
        for entry in filter(
            lambda entry: 1 <= (entry.rank_swiss or 0) <= ceil(len(tournament.entries()) * 0.3),
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


def cluster_decklists(decks: Set[Decklist], k: int, f: TextIOWrapper):
    """Cluster the given decks and write the output markdown to the passed file."""
    cards = all_cards(decks)
    vectored_decklists = [vectorise_decklist(cards, deck) for deck in decks]

    km = KMeans(n_clusters=k).fit(vectored_decklists)
    labels = list(km.labels_)
    decks_with_labels = list(zip(decks, labels))
    for label in range(0, k):
        f.write(f"\n### {label}\n\n")
        for (deck, deck_label) in decks_with_labels:
            if label == deck_label:
                f.write(f"* [{deck.name}](https://netrunnerdb.com/en/decklist/{deck.uuid})\n")


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


if __name__ == "__main__":
    main()
