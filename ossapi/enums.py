from dataclasses import dataclass
from typing import Optional, List, Any
from enum import IntFlag


from ossapi.utils import EnumModel, ListEnumMeta, Datetime, Model, BaseModel

# ================
# Documented Enums
# ================

class ProfilePage(EnumModel):
    ME = "me"
    RECENT_ACTIVITY = "recent_activity"
    BEATMAPS = "beatmaps"
    HISTORICAL = "historical"
    KUDOSU = "kudosu"
    TOP_RANKS = "top_ranks"
    MEDALS = "medals"

class GameMode(EnumModel):
    STD    = "osu"
    TAIKO  = "taiko"
    CTB    = "fruits"
    MANIA  = "mania"

class ScoreType(EnumModel):
    BEST = "best"
    FIRST = "first"
    RECENT = "recent"

class RankingFilter(EnumModel):
    ALL = "all"
    FRIENDS = "friends"

class RankingType(EnumModel):
    CHARTS = "spotlight"
    COUNTRY = "country"
    PERFORMANCE = "performance"
    SCORE = "score"

class UserLookupKey(EnumModel):
    ID = "id"
    USERNAME = "username"

# for reasons I don't fully understand, we can't do
# ``PlayStyles(IntFlagModel, metaclass=ListEnumMeta)`` and must instead do this,
# with two separate classes. Possibly because when using an enum metaclass, its
# superclass must be a direct enum class like ``IntFlag``, and not a subclass
# like ``IntFlagModel``? Weird territory here.
# The error thrown when using ``IntFlagModel`` is:
# ``TypeError: object.__new__(PlayStyles) is not safe, use int.__new__()``
class PlayStyles(BaseModel, IntFlag, metaclass=ListEnumMeta):
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

class RankStatus(EnumModel):
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

class UserAccountHistoryType(EnumModel):
    NOTE = "note"
    RESTRICTION = "restriction"
    SILENCE = "silence"

class MessageType(EnumModel):
    DISQUALIFY = "disqualify"
    HYPE = "hype"
    MAPPER_NOTE = "mapper_note"
    NOMINATION_RESET = "nomination_reset"
    PRAISE = "praise"
    PROBLEM = "problem"
    REVIEW = "review"
    SUGGESTION = "suggestion"

class BeatmapsetEventType(EnumModel):
    APPROVE =  "approve"
    BEATMAP_OWNER_CHANGE = "beatmap_owner_change"
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

class BeatmapsetDownload(EnumModel):
    ALL = "all"
    NO_VIDEO = "no_video"
    DIRECT = "direct"

class UserListFilters(EnumModel):
    ALL = "all"
    ONLINE = "online"
    OFFLINE = "offline"

class UserListSorts(EnumModel):
    LAST_VISIT = "last_visit"
    RANK = "rank"
    USERNAME = "username"

class UserListViews(EnumModel):
    CARD = "card"
    LIST = "list"
    BRICK = "brick"

class KudosuAction(EnumModel):
    # TODO ideally these wouldn't be prefixed with ``vote``. They aren't
    # documented as such in https://osu.ppy.sh/docs/index.html#kudosuhistory,
    # but that's what the api returns
    GIVE = "vote.give"
    RESET = "vote.reset"
    REVOKE = "vote.revoke"

class UserBeatmapType(EnumModel):
    FAVOURITE = "favourite"
    GRAVEYARD = "graveyard"
    LOVED = "loved"
    MOST_PLAYED = "most_played"
    RANKED = "ranked"
    PENDING = "pending"

class BeatmapDiscussionPostSort(EnumModel):
    NEW = "id_desc"
    OLD = "id_asc"

class EventType(EnumModel):
    ACHIEVEMENT = "achievement"
    BEATMAP_PLAYCOUNT = "beatmapPlaycount"
    BEATMAPSET_APPROVE = "beatmapsetApprove"
    BEATMAPSET_DELETE = "beatmapsetDelete"
    BEATMAPSET_REVIVE = "beatmapsetRevive"
    BEATMAPSET_UPDATE = "beatmapsetUpdate"
    BEATMAPSET_UPLOAD = "beatmapsetUpload"
    RANK = "rank"
    RANK_LOST = "rankLost"
    USER_SUPPORT_FIRST = "userSupportFirst"
    USER_SUPPORT_AGAIN = "userSupportAgain"
    USER_SUPPORT_GIFT = "userSupportGift"
    USERNAME_CHANGE = "usernameChange"

# TODO this is just a subset of ``RankStatus``, and is only (currently) used for
# ``EventType.BEATMAPSET_APPROVE``. Find some way to de-duplicate? Could move to
# ``RankStatus``, but then how to enforce taking on only a subset of values?
class BeatmapsetApproval(EnumModel):
    RANKED = "ranked"
    APPROVED = "approved"
    QUALIFIED = "qualified"
    LOVED = "loved"


# ==================
# Undocumented Enums
# ==================


class UserRelationType(EnumModel):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserRelationTransformer.php#L20
    FRIEND = "friend"
    BLOCK = "block"

class Grade(EnumModel):
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
class Failtimes(Model):
    exit: Optional[List[int]]
    fail: Optional[List[int]]

@dataclass
class Ranking(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/CountryTransformer.php#L30
    active_users: int
    play_count: int
    ranked_score: int
    performance: int

@dataclass
class Country(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/CountryTransformer.php#L10
    code: str
    name: str

    # optional fields
    # ---------------
    display: Optional[int]
    ranking: Optional[Ranking]

@dataclass
class Cover(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserCompactTransformer.php#L158
    custom_url: Optional[str]
    url: str
    # api should really return an int here instead...open an issue?
    id: Optional[str]


@dataclass
class ProfileBanner(Model):
    id: int
    tournament_id: int
    image: str

@dataclass
class UserAccountHistory(Model):
    description: Optional[str]
    type: UserAccountHistoryType
    timestamp: Datetime
    length: int


@dataclass
class UserBadge(Model):
    awarded_at: Datetime
    description: str
    image_url: str
    url: str

@dataclass
class GroupDescription(Model):
    html: str
    markdown: str

@dataclass
class UserGroup(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserGroupTransformer.php#L10
    id: int
    identifier: str
    name: str
    short_name: str
    colour: Optional[str]
    description: Optional[GroupDescription]
    playmodes: Optional[List[GameMode]]
    is_probationary: bool
    has_listing: bool
    has_playmodes: bool

@dataclass
class Covers(Model):
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
class Statistics(Model):
    count_50: int
    count_100: int
    count_300: int
    count_geki: int
    count_katu: int
    count_miss: int

@dataclass
class Availability(Model):
    download_disabled: bool
    more_information: Optional[str]

@dataclass
class Hype(Model):
    current: int
    required: int

@dataclass
class Nominations(Model):
    current: int
    required: int

@dataclass
class Kudosu(Model):
    total: int
    available: int

@dataclass
class KudosuGiver(Model):
    url: str
    username: str

@dataclass
class KudosuPost(Model):
    url: Optional[str]
    # will be "[deleted beatmap]" for deleted beatmaps. TODO codify this
    # somehow? another enum perhaps? see
    # https://osu.ppy.sh/docs/index.html#kudosuhistory
    title: str

@dataclass
class KudosuVote(Model):
    user_id: int
    score: int

@dataclass
class EventUser(Model):
    username: str
    url: str
    previousUsername: Optional[str]

@dataclass
class EventBeatmap(Model):
    title: str
    url: str

@dataclass
class EventBeatmapset(Model):
    title: str
    url: str

@dataclass
class EventAchivement(Model):
    icon_url: str
    id: int
    name: str
    # TODO ``grouping`` can probably be enumified (example value: "Dedication"),
    # need to find full list first though
    grouping: str
    ordering: int
    slug: str
    description: str
    mode: GameMode
    instructions: Optional[Any]

@dataclass
class GithubUser(Model):
    display_name: str
    github_url: Optional[str]
    id: Optional[int]
    osu_username: Optional[str]
    user_id: Optional[int]
    user_url: Optional[str]

@dataclass
class ChangelogSearch(Model):
    from_: Optional[str]
    limit: int
    max_id: Optional[int]
    stream: Optional[str]
    to: Optional[str]

# ===================
# Undocumented Models
# ===================

@dataclass
class UserMonthlyPlaycount(Model):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserMonthlyPlaycountTransformer.php
    start_date: Datetime
    count: int

@dataclass
class UserPage(Model):
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserCompactTransformer.php#L270
    html: str
    raw: str

@dataclass
class UserLevel(Model):
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserStatisticsTransformer.php#L27
    current: int
    progress: int

@dataclass
class UserGradeCounts(Model):
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserStatisticsTransformer.php#L43
    ss: int
    ssh: int
    s: int
    sh: int
    a: int

@dataclass
class UserReplaysWatchedCount(Model):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserReplaysWatchedCountTransformer.php
    start_date: Datetime
    count: int

@dataclass
class UserAchievement(Model):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserAchievementTransformer.php#L10
    achieved_at: Datetime
    achievement_id: int

@dataclass
class UserProfileCustomization(Model):
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
class RankHistory(Model):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/RankHistoryTransformer.php
    mode: GameMode
    data: List[int]

@dataclass
class Weight(Model):
    percentage: float
    pp: float
