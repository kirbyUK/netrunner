from typing import Any, Dict, Optional

import requests

from netrunner.netrunnerdb.api import _API_ENDPOINT
from netrunner.netrunnerdb.card import Card


class Decklist:
    """Class representing a single Netrunner decklist."""

    def __init__(self, id: Optional[int] = None, uuid: Optional[str] = None) -> None:
        """
        Constructor.

        :param id: The decklist numerical ID.
        :param uuid: The decklist UUID.
        """
        if id is not None:
            r = requests.get(f"{_API_ENDPOINT}/decklist/{id}")
        elif uuid is not None:
            r = requests.get(f"{_API_ENDPOINT}/decklist/{uuid}")
        else:
            raise Exception
        
        json = r.json()
        if ("success" not in json or not json["success"] or
            "total" not in json or json["total"] < 1 or
            "data" not in json):
            raise Exception
        self.decklist = json["data"][0]
        self.cards_dict = { Card(id): quantity for id, quantity in self.decklist["cards"].items() }

    def __eq__(self, other: Any) -> bool:
        return type(other) is Decklist and self.id == other.id

    def __hash__(self) -> int:
        return self.id

    @property
    def id(self) -> int:
        return self.decklist["id"]

    @property
    def uuid(self) -> str:
        return self.decklist["uuid"]
    
    @property
    def date_creation(self) -> str:
        return self.decklist["date_creation"]
    
    @property
    def date_update(self) -> str:
        return self.decklist["date_update"]
    
    @property
    def name(self) -> str:
        return self.decklist["name"]
    
    @property
    def description(self) -> str:
        return self.decklist["description"]
    
    @property
    def user_id(self) -> int:
        return self.decklist["user_id"]
    
    @property
    def user_name(self) -> str:
        return self.decklist["user_name"]
    
    @property
    def tournament_badge(self) -> bool:
        return self.decklist["tournament_badge"]
    
    @property
    def cards(self) -> Dict[Card, int]:
        return self.cards_dict
    
    @property
    def mwl_code(self) -> str:
        return self.decklist["mwl_code"]
