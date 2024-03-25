from typing import Any, Dict, Optional

class Entry:
    """A single entrant in an AlwaysBeRunning.net event."""

    def __init__(self, entry: Dict[str, Any]) -> None:
        self.entry = entry

    def __eq__(self, other: Any) -> bool:
        return (type(other) is Entry and
                (self.user_id is not None and
                 other.user_id is not None and
                 self.user_id == other.user_id) or
                (self.user_id is None and
                 other.user_id is None and
                 self.user_import_name == other.user_import_name))

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"Entry({self.user_name if self.user_name is not None else self.user_import_name})"
    
    # Player related properties

    @property
    def user_id(self) -> Optional[int]:
        return self.entry.get("user_id")
    
    @property
    def user_name(self) -> Optional[str]:
        return self.entry.get("user_name")

    @property
    def user_import_name(self) -> Optional[str]:
        return self.entry.get("user_import_name")
    
    # Rank properties

    @property
    def rank_swiss(self) -> Optional[int]:
        return self.entry.get("rank_swiss")
    
    @property
    def rank_top(self) -> Optional[int]:
        return self.entry.get("rank_top")
    
    # Deck related properties

    @property
    def runner_deck_title(self) -> Optional[str]:
        return self.entry.get("runner_deck_title") or None
    
    @property
    def runner_deck_identity_id(self) -> Optional[str]:
        return self.entry.get("runner_deck_identity_id") or None
    
    @property
    def runner_deck_url(self) -> Optional[str]:
        return self.entry.get("runner_deck_url") or None
    
    @property
    def runner_deck_identity_title(self) -> Optional[str]:
        return self.entry.get("runner_deck_identity_title") or None
    
    @property
    def runner_deck_identity_faction(self) -> Optional[str]:
        return self.entry.get("runner_deck_identity_faction") or None
    
    @property
    def corp_deck_title(self) -> Optional[str]:
        return self.entry.get("corp_deck_title") or None
    
    @property
    def corp_deck_identity_id(self) -> Optional[str]:
        return self.entry.get("corp_deck_identity_id") or None
    
    @property
    def corp_deck_url(self) -> Optional[str]:
        return self.entry.get("corp_deck_url") or None
    
    @property
    def corp_deck_identity_title(self) -> Optional[str]:
        return self.entry.get("corp_deck_identity_title") or None
    
    @property
    def corp_deck_identity_faction(self) -> Optional[str]:
        return self.entry.get("corp_deck_identity_faction") or None