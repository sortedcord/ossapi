from dataclasses import dataclass
from enum import Enum, IntFlag
from typing import Optional, List, Any

from ossapi.utils import ListEnumMeta, Datetime

# ================
# Documented Enums
# ================

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

class ScoreType(Enum):
    BEST = "best"
    FIRST = "first"
    RECENT = "recent"

class RankingFilter(Enum):
    ALL = "all"
    FRIENDS = "friends"

class RankingType(Enum):
    CHARTS = "spotlight"
    COUNTRY = "country"
    PERFORMANCE = "performance"
    SCORE = "score"


class PlayStyles(IntFlag, metaclass=ListEnumMeta):
    MOUSE = 1
    KEYBOARD = 2
    TABLET = 4
    TOUCH = 8

    @classmethod
    def _missing_(cls, value):
        """
        Our backing values are ints (which is necessary for us to use a flag)
        but we also want to be able to instantiate with the strings the api
        returns.
        """
        if value == "mouse":
            return PlayStyles.MOUSE
        if value == "keyboard":
            return PlayStyles.KEYBOARD
        if value == "tablet":
            return PlayStyles.TABLET
        if value == "touch":
            return PlayStyles.TOUCH
        return super()._missing_(value)

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
        so if we try to instantiate with a string, return the corresponding
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

class MessageType(Enum):
    DISQUALIFY = "disqualify"
    HYPE = "hype"
    MAPPER_NOTE = "mapper_note"
    NOMINATION_RESET = "nomination_reset"
    PRAISE = "praise"
    PROBLEM = "problem"
    REVIEW = "review"
    SUGGESTION = "suggestion"

class BeatmapsetEventType(Enum):
    APPROVE =  "approve"
    DISCUSSION_DELETE =  "discussion_delete"
    DISCUSSION_LOCK =  "discussion_lock"
    DISCUSSION_POST_DELETE =  "discussion_post_delete"
    DISCUSSION_POST_RESTORE =  "discussion_post_restore"
    DISCUSSION_RESTORE =  "discussion_restore"
    DISCUSSION_UNLOCK = "discussion_unlock"
    DISQUALIFY = "disqualify"
    DISQUALIFY_LEGACY = "disqualify_legacy"
    GENRE_EDIT = "genre_edit"
    ISSUE_REOPEN = "issue_reopen"
    ISSUE_RESOLVE = "issue_resolve"
    KUDOSU_ALLOW = "kudosu_allow"
    KUDOSU_DENY = "kudosu_deny"
    KUDOSU_GAIN = "kudosu_gain"
    KUDOSU_LOST = "kudosu_lost"
    KUDOSU_RECALCULATE = "kudosu_recalculate"
    LANGUAGE_EDIT = "language_edit"
    LOVE = "love"
    NOMINATE = "nominate"
    NOMINATE_MODES = "nominate_modes"
    NOMINATION_RESET = "nomination_reset"
    QUALIFY = "qualify"
    RANK = "rank"
    REMOVE_FROM_LOVED = "remove_from_loved"
    NSFW_TOGGLE = "nsfw_toggle"

class BeatmapsetDownload(Enum):
    ALL = "all"
    NO_VIDEO = "no_video"
    DIRECT = "direct"

class UserListFilters(Enum):
    ALL = "all"
    ONLINE = "online"
    OFFLINE = "offline"

class UserListSorts(Enum):
    LAST_VISIT = "last_visit"
    RANK = "rank"
    USERNAME = "username"

class UserListViews(Enum):
    CARD = "card"
    LIST = "list"
    BRICK = "brick"


# ==================
# Undocumented Enums
# ==================


class UserRelationType(Enum):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserRelationTransformer.php#L20
    FRIEND = "friend"
    BLOCK = "block"

class Grade(Enum):
    SSH = "XH"
    SS = "X"
    SH = "SH"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

# =================
# Documented Models
# =================


@dataclass
class Failtimes:
    exit: Optional[List[int]]
    fail: Optional[List[int]]

@dataclass
class Ranking:
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/CountryTransformer.php#L30
    active_users: int
    play_count: int
    ranked_score: int
    performance: int

@dataclass
class Country:
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/CountryTransformer.php#L10
    code: str
    name: str

    # optional fields
    # ---------------
    display: Optional[int]
    ranking: Optional[Ranking]

@dataclass
class Cover:
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserCompactTransformer.php#L158
    custom_url: str
    url: str
    # api should really return an int here instead...open an issue?
    id: str


@dataclass
class ProfileBanner:
    id: int
    tournament_id: int
    image: str

@dataclass
class UserAccountHistory:
    description: str
    type: UserAccountHistoryType
    timestamp: Datetime
    length: int


@dataclass
class UserBadge:
    awarded_at: Datetime
    description: str
    image_url: str
    url: str

@dataclass
class UserGroup:
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserGroupTransformer.php#L10
    id: int
    identifier: str
    name: str
    short_name: str
    description: str
    colour: str
    playmodes: Optional[List[GameMode]]
    is_probationary: bool

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

@dataclass
class Kudosu:
    total: int
    available: int


# ===================
# Undocumented Models
# ===================

@dataclass
class UserMonthlyPlaycount:
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserMonthlyPlaycountTransformer.php
    start_date: Datetime
    count: int

@dataclass
class UserPage:
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserCompactTransformer.php#L270
    html: str
    raw: str

@dataclass
class UserLevel:
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserStatisticsTransformer.php#L27
    current: int
    progress: int

@dataclass
class UserGradeCounts:
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserStatisticsTransformer.php#L43
    ss: int
    ssh: int
    s: int
    sh: int
    a: int

@dataclass
class UserReplaysWatchedCount:
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserReplaysWatchedCountTransformer.php
    start_date: Datetime
    count: int

@dataclass
class UserAchievement:
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserAchievementTransformer.php#L10
    achieved_at: Datetime
    achievement_id: int

@dataclass
class UserProfileCustomization:
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserCompactTransformer.php#L363
    # https://github.com/ppy/osu-web/blob/master/app/Models/UserProfileCustomization.php
    audio_autoplay: Optional[bool]
    audio_muted: Optional[bool]
    audio_volume: Optional[int]
    beatmapset_download: Optional[BeatmapsetDownload]
    beatmapset_show_nsfw: Optional[bool]
    beatmapset_title_show_original: Optional[bool]
    comments_show_deleted: Optional[bool]
    forum_posts_show_deleted: bool
    ranking_expanded: bool
    user_list_filter: Optional[UserListFilters]
    user_list_sort: Optional[UserListSorts]
    user_list_view: Optional[UserListViews]

@dataclass
class RankHistory:
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/RankHistoryTransformer.php
    mode: GameMode
    data: List[int]

@dataclass
class Weight:
    percentage: float
    pp: float
