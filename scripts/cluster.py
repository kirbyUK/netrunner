from datetime import date
from netrunner.netrunnerdb.card import Card
from netrunner.netrunnerdb.decklist import Decklist
from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning
from netrunner.alwaysberunning.event import Event
from typing import List, Set

from sklearn.cluster import KMeans


def main():
    decks = set()
    abr = AlwaysBeRunning()
    for result in filter(
        lambda event:
            ((event.registration_count or 0) >= 24 and
             (event.format or "") == "standard" and
             (event.cardpool or "") == "The Automata Initiative" and
             event.title != "Nova vs Ampère Only - Standard Asynch"),
        all_events(abr,
                   date(2023, 8, 5),   # 2023-08-05: 2023 APAC Continentals
                   date(2024, 2, 19)  # 2024-02-19: Bristol 2024 Q1)
    )):
        print(result.title)
        for entry in filter(
            lambda entry: 1 <= (entry.rank_swiss or 0) <= 16,
            result.entries()
        ):
            if entry.runner_deck_url is not None:
                decks.add(Decklist(url=entry.runner_deck_url))

    cards = all_cards(decks)
    vectored_decklists = [vectorise_decklist(cards, deck) for deck in decks]

    clusters = 10
    km = KMeans(n_clusters=clusters).fit(vectored_decklists)
    labels = list(km.labels_)
    decks_with_labels = list(zip(decks, labels))
    for label in range(0, clusters):
        print(label)
        for (deck, deck_label) in decks_with_labels:
            if label == deck_label:
                print(f"\t{deck.uuid} {deck.name}")


def all_events(abr: AlwaysBeRunning, start: date, end: date) -> List[Event]:
    all_events = []
    offset = 0
    events = abr.results(offset=offset, start=start, end=end)
    while len(events) >= 500:
        all_events.extend(events)
        events = abr.results(offset=offset, start=start, end=end)
        offset += 500

    return all_events


def all_cards(all_decklists: Set[Decklist]) -> List[Card]:
    return sorted(list(set([card
                            for decklist in all_decklists
                            for card in decklist.cards])),
                  key=lambda card: card.title)


def vectorise_decklist(all_cards: List[Card], decklist: Decklist) -> List[int]:
    vector = [0] * len(all_cards)
    for card, quantity in decklist.cards.items():  
        vector[all_cards.index(card)] = quantity

    return vector


if __name__ == "__main__":
    main()
