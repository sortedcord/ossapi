from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional, List

class ProfilePage(Enum):
    ME = "me"
    RECENT_ACTIVITY = "recent_activity"
    BEATMAPS = "beatmaps"
    HISTORICAL = "historical"
    KUDOSU = "kudosu"
    TOP_RANKS = "top_ranks"
    MEDALS = "medals"

class GameMode(Enum):
    STD    = "osu"
    TAIKO  = "taiko"
    CTB    = "fruits"
    MANIA  = "mania"

class RankStatus(Enum):
    GRAVEYARD = -2
    WIP = -1
    PENDING = 0
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4

    @classmethod
    def _missing_(cls, value):
        """
        The api can return ``RankStatus`` values as either an int or a string,
        so if we try to instantiatte with a string, return the corresponding
        enum attribute.
        """
        if value == "graveyard":
            return cls(-2)
        if value == "wip":
            return cls(-1)
        if value == "pending":
            return cls(0)
        if value == "ranked":
            return cls(1)
        if value == "approved":
            return cls(2)
        if value == "qualified":
            return cls(3)
        if value == "loved":
            return cls(4)
        return super()._missing_(value)

class UserAccountHistoryType(Enum):
    NOTE = "note"
    RESTRICTION = "restriction"
    SILENCE = "silence"


@dataclass
class Failtimes:
    exit: Optional[List[int]]
    fail: Optional[List[int]]

@dataclass
class Country:
    code: str
    name: str

@dataclass
class Cover:
    custom_url: str
    url: str
    id: int


@dataclass
class ProfileBanner:
    id: int
    tournament_id: int
    image: str

@dataclass
class UserAccountHistory:
    id: int
    type: UserAccountHistoryType
    timestamp: datetime
    length: int


@dataclass
class UserBadge:
    awarded_at: datetime
    description: str
    image_url: str
    url: str

@dataclass
class UserGroup:
    id: int
    identifier: str
    is_probationary: bool
    name: str
    short_name: str
    description: str
    colour: str
    playmodes: Optional[List[GameMode]]

@dataclass
class Covers:
    """
    https://osu.ppy.sh/docs/index.html#beatmapsetcompact-covers
    """
    cover: str
    cover_2x: str
    card: str
    card_2x: str
    list: str
    list_2x: str
    slimcover: str
    slimcover_2x: str

@dataclass
class Statistics:
    count_50: int
    count_100: int
    count_300: int
    count_geki: int
    count_katu: int
    count_miss: int

@dataclass
class Availability:
    download_disabled: bool
    more_information: Optional[str]

@dataclass
class Hype:
    current: int
    required: int

@dataclass
class Nominations:
    current: int
    required: int
