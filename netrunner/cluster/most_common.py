from netrunner.netrunnerdb.card import Card
from netrunner.netrunnerdb.decklist import Decklist
from typing import Dict, List, Tuple


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
