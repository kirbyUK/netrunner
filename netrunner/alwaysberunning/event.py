from typing import Any, Dict, List, Optional

import requests

from netrunner.alwaysberunning.api import _API_ENDPOINT
from netrunner.alwaysberunning.entry import Entry

class Event:
    """A single AlwaysBeRunning.net event."""

    def __init__(self, event: Dict[str, Any]) -> None:
        self.event = event

    def __eq__(self, other: Any) -> bool:
        return type(other) is Event and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Event({self.title})"
    
    def entries(self) -> List[Entry]:
        r = requests.get(f"{_API_ENDPOINT}/entries", params={"id": self.id})
        return [Entry(e) for e in r.json()]

    # General properties

    @property
    def id(self) -> int:
        return int(self.event["id"])
    
    @property
    def title(self) -> str:
        return self.event["title"]
    
    @property
    def contact(self) -> Optional[str]:
        return self.event.get("contact") 
    
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
        return self.event.get("url")
    
    @property
    def link_facebook(self) -> Optional[str]:
        return self.event.get("link_facebook")
    
    # Event creator related properties

    # Location related properties

    # Tournament related properties

    # Concluded tournament properties

    # Recurring event properties

    # Multiple day event properties