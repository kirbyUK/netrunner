from typing import Any, Dict, List, Optional

import datetime
import requests

from netrunner.alwaysberunning.api import _API_ENDPOINT
from netrunner.alwaysberunning.entry import Entry

class Event:
    """A single AlwaysBeRunning.net event."""

    def __init__(self, event: Dict[str, Any]) -> None:
        self.event = event
        self._entries: Optional[List[Entry]] = None

    def __eq__(self, other: Any) -> bool:
        return type(other) is Event and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Event({self.title})"
    
    def entries(self) -> List[Entry]:
        if self._entries is None:
            r = requests.get(f"{_API_ENDPOINT}/entries", params={"id": self.id})
            self._entries = [Entry(self.id, e) for e in r.json()]
        return self._entries

    # General properties

    @property
    def id(self) -> int:
        return int(self.event["id"])
    
    @property
    def title(self) -> str:
        return self.event["title"]
    
    @property
    def contact(self) -> Optional[str]:
        return self.event.get("contact") or None
    
    @property
    def approved(self) -> Optional[int]:
        return self.event.get("approved")
    
    @property
    def registration_count(self) -> Optional[int]:
        return self.event.get("registration_count")
    
    @property
    def photos(self) -> Optional[int]:
        return self.event.get("photos")
    
    @property
    def url(self) -> Optional[str]:
        return self.event.get("url") or None
    
    @property
    def link_facebook(self) -> Optional[str]:
        return self.event.get("link_facebook") or None
    
    # Event creator related properties

    # Location related properties

    # Tournament related properties

    @property
    def cardpool(self) -> Optional[str]:
        return self.event.get("cardpool") or None
    
    @property
    def date(self) -> Optional[datetime.date]:
        date = self.event.get("date")
        if date is not None:
            return datetime.datetime.strptime(date, "%Y.%m.%d.").date()
        return None
    
    @property
    def type(self) -> Optional[str]:
        return self.event.get("type") or None

    @property
    def format(self) -> Optional[str]:
        return self.event.get("format") or None
    
    @property
    def concluded(self) -> Optional[bool]:
        return self.event.get("concluded")
    
    @property
    def charity(self) -> Optional[bool]:
        return self.event.get("charity")

    # Concluded tournament properties

    # Recurring event properties

    # Multiple day event properties