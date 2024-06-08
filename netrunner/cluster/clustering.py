from netrunner.netrunnerdb.card import Card
from netrunner.netrunnerdb.decklist import Decklist
from sklearn.cluster import DBSCAN
from typing import Dict, List, Set


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
