from enum import Enum
from datetime import date
from typing import List, Optional

import requests

from netrunner.alwaysberunning.api import _API_ENDPOINT
from netrunner.alwaysberunning.event import Event

class TournamentType(Enum):
    GNK = 1
    StoreChampionship = 2
    RegionalChampionship = 3
    NationalChamptionship = 4
    WorldsChampionship = 5
    CommunityTournament = 6
    OnlineEvent = 7
    NonTournamentEvent = 8
    ContinentalChampionship = 9
    TeamTournament = 10
    CircuitOpener = 11
    AsynchronousTournament = 12
    CircuitBreaker = 13
    IntercontinentalChampionship = 14
    PlayersCircuit = 15

class AlwaysBeRunning:
    """Wrapper around alwaysberunning.net."""

    def results(self,
                offset: Optional[int] = None,
                start: Optional[date] = None,
                end: Optional[date] = None,
                tournament_type: Optional[TournamentType] = None,
                cardpool: Optional[str] = None,
                recur: Optional[bool] = None,
                country: Optional[str] = None,
                include_online: Optional[bool] = None,
                state: Optional[str] = None,
                creator: Optional[int] = None,
                videos: Optional[bool] = None,
                foruser: Optional[int] = None,
                concluded: Optional[bool] = None,
                approved: Optional[bool] = None,
                desc: Optional[bool] = None) -> List[Event]:
        
        params = { "limit": 500 }

        # Construct filter arguments
        if offset is not None:
            params["offset"] = offset
        if start is not None:
            params["start"] = start.isoformat()
        if end is not None:
            params["end"] = end.isoformat()
        if tournament_type is not None:
            params["type"] = int(tournament_type)
        if cardpool is not None:
            params["cardpool"] = cardpool
        if recur is not None:
            params["recur"] = int(recur)
        if country is not None:
            params["country"] = country
        if include_online is not None:
            params["include_online"] = int(include_online)
        if state is not None:
            params["state"] = state
        if creator is not None:
            params["creator"] = creator
        if videos is not None:
            params["videos"] = int(videos)
        if foruser is not None:
            params["foruser"] = foruser
        if concluded is not None:
            params["concluded"] = int(concluded)
        if approved is not None:
            params["approved"] = int(approved)
        if desc is not None:
            params["desc"] = int(desc)

        r = requests.get(f"{_API_ENDPOINT}/tournaments/results", params=params)
        json = r.json()
        return [Event(e) for e in json]
