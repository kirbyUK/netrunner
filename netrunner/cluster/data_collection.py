from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning
from netrunner.alwaysberunning.event import Event
from netrunner.netrunnerdb.decklist import Decklist
from math import floor
import sys
from typing import Optional, List, Set, Tuple


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
