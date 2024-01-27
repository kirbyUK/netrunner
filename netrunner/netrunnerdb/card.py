from typing import Any, List, Optional, Union

import requests

from netrunner.netrunnerdb.api import _API_ENDPOINT


class Card:
    """Class representing a single Netrunner card."""

    def __init__(self, id: Union[int, str]):
        """
        Constructor.

        :param id: The id of the card to fetch.
        """
        r = requests.get(f"{_API_ENDPOINT}/card/{id}")
        
        json = r.json()
        if ("success" not in json or not json["success"] or
            "total" not in json or json["total"] < 1 or
            "data" not in json):
            raise Exception
        self.card = json["data"][0]

    def __eq__(self, other: Any) -> bool:
        return type(other) is Card and self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)

    def __repr__(self) -> str:
        return f"Card({self.stripped_title})"

    @property
    def code(self) -> str:
        return self.card["code"]

    @property
    def cost(self) -> Optional[int]:
        return self.card["cost"] if "cost" in self.card else None

    @property
    def deck_limit(self) -> Optional[int]:
        return self.card["deck_limit"] if "deck_limit" in self.card else None

    @property
    def faction_code(self) -> str:
        return self.card["faction_code"]

    @property
    def illustrator(self) -> str:
        return self.card["illustrator"]

    @property
    def keywords(self) -> Optional[List[str]]:
        return self.card["keywords"].split(" - ") if "keywords" in self.card else None

    @property
    def side_code(self) -> str:
        return self.card["side_code"]

    @property
    def stripped_text(self) -> str:
        return self.card["stripped_text"]

    @property
    def stripped_title(self) -> str:
        return self.card["stripped_title"]

    @property
    def text(self) -> str:
        return self.card["text"]

    @property
    def title(self) -> str:
        return self.card["title"]
