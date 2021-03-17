from dataclasses import dataclass
from typing import Optional, TypeVar, Generic, Any, List
from datetime import datetime
from types import SimpleNamespace

from ossapi.mod import Mod
from ossapi.enums import (Country, Cover, ProfilePage, UserAccountHistory,
    UserBadge, ProfileBanner, UserGroup, GameMode, RankStatus, Failtimes,
    Covers, Statistics, Availability, Hype, Nominations)

T = TypeVar("T")


"""
a type hint of ``Optional[Any]`` or ``Any`` means that I don't know what type it
is, not that the api actually lets any type be returned there.
"""

@dataclass
class UserCompact:
    """
    https://osu.ppy.sh/docs/index.html#usercompact
    """
    # required fields
    # ---------------
    avatar_url: str
    country_code: str
    default_group: str
    id: int
    is_active: bool
    is_bot: bool
    is_deleted: bool
    is_online: bool
    is_supporter: bool
    last_visit: bool
    pm_friends_only: bool
    profile_colour: str
    username: str

    # optional fields
    # ---------------
    account_history: Optional[List[UserAccountHistory]]
    active_tournament_banner: Optional[ProfileBanner]
    badges: Optional[List[UserBadge]]
    beatmap_playcounts_count: Optional[int]
    blocks: Optional[Any]
    country: Optional[Country]
    cover: Optional[Cover]
    favourite_beatmapset_count: Optional[int]
    follower_count: Optional[int]
    friends: Optional[Any]
    graveyard_beatmapset_count: Optional[int]
    groups: Optional[List[UserGroup]]
    is_admin: Optional[bool]
    is_bng: Optional[bool]
    is_full_bn: Optional[bool]
    is_gmt: Optional[bool]
    is_limited_bn: Optional[bool]
    is_moderator: Optional[bool]
    is_nat: Optional[bool]
    is_restricted: Optional[bool]
    is_silenced: Optional[bool]
    loved_beatmapset_count: Optional[int]
    monthly_playcounts: Optional[List[None]]
    page: Optional[Any]
    previous_usernames: Optional[Any]
    ranked_and_approved_beatmapset_count: Optional[Any]
    replays_watched_counts: Optional[Any]
    scores_best_count: Optional[int]
    scores_first_count: Optional[int]
    scores_recent_count: Optional[int]
    statistics: Optional[Any]
    statistics_rulesets: Optional[Any]
    support_level: Optional[Any]
    unranked_beatmapset_count: Optional[Any]
    unread_pm_count: Optional[Any]
    user_achievements: Optional[Any]
    user_preferences: Optional[Any]
    rank_history: Optional[Any]


@dataclass
class User(UserCompact):
    cover_url: str
    discord: Optional[str]
    has_supported: bool
    interests: Optional[str]
    join_date: datetime
    kudosu: Any
    location: Optional[str]
    max_blocks: int
    max_friends: int
    occupation: Optional[str]
    playmode: str
    playstyle: List[str]
    post_count: int
    profile_order: List[ProfilePage]
    title: Optional[str]
    twitter: Optional[str]
    website: Optional[str]



@dataclass
class BeatmapCompact:
    # required fields
    # ---------------
    difficulty_rating: float
    id: int
    mode: GameMode
    status: RankStatus
    total_length: int
    version: str

    # optional fields
    # ---------------
    # ``BeatmapCompact`` and ``BeatmapsetCompact`` are mutually dependent, so
    # set a dummy type here and we'll update it to the real type after
    # ``BeatmapsetCompact`` is defined.
    beatmapset: Optional[Any] # Optional[BeatmapsetCompact]
    checksum: Optional[str]
    failtimes: Optional[Failtimes]
    max_combo: Optional[int]


@dataclass
class Beatmap(BeatmapCompact):
    total_length: int
    version: str
    accuracy: int
    ar: int
    beatmapset_id: int
    bpm: int
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: int
    deleted_at: str
    drain: int
    hit_length: int
    is_scoreable: bool
    last_updated: datetime
    mode_int: int
    passcount: int
    playcount: int
    ranked: int
    url: str

    # overridden fields
    # -----------------
    beatmapset: Optional[Any] # Optional[Beatmapset]


@dataclass
class BeatmapsetCompact:
    """
    https://osu.ppy.sh/docs/index.html#beatmapsetcompact
    """
    # required fields
    # ---------------
    artist: str
    artist_unicode: str
    covers: Covers
    creator: str
    favourite_count: int
    id: int
    play_count: int
    preview_url: str
    source: str
    status: RankStatus
    title: str
    title_unicode: str
    user_id: int
    video: str
    # documented as being in ``Beatmapset`` only, but returned by
    # ``api.beatmapset_events`` which uses a ``BeatmapsetCompact``.
    hype: Hype
    # entirely undocumented
    nsfw: bool

    # optional fields
    # ---------------
    beatmaps: Optional[List[Beatmap]]
    converts: Optional[Any]
    current_user_attributes: Optional[Any]
    description: Optional[Any]
    discussions: Optional[Any]
    events: Optional[Any]
    genre: Optional[Any]
    has_favourited: Optional[bool]
    language: Optional[Any]
    nominations: Optional[Any]
    ratings: Optional[Any]
    recent_favourites: Optional[Any]
    related_users: Optional[Any]
    user: Optional[UserCompact]

@dataclass
class Beatmapset(BeatmapsetCompact):
    availability: Availability
    bpm: int
    can_be_hyped: bool
    discussion_enabled: bool
    discussion_locked: bool
    is_scoreable: bool
    last_updated: datetime
    legacy_thread_url: Optional[str]
    nominations_summary: Nominations
    ranked: RankStatus
    ranked_date: Optional[datetime]
    storyboard: bool
    submitted_date: Optional[datetime]
    tags: str


# see the comment on BeatmapCompact.beatmapset for reasoning
# pylint: disable=no-member
BeatmapCompact.__annotations__["beatmapset"] = Optional[BeatmapsetCompact]
Beatmap.__annotations__["beatmapset"] = Optional[Beatmapset]
# pylint: enable=no-member

@dataclass
class Match:
    pass

@dataclass
class Score:
    """
    https://osu.ppy.sh/docs/index.html#score
    """
    id: int
    best_id: int
    user_id: int
    accuracy: float
    mods: Mod
    score: int
    max_combo: int
    perfect: bool
    statistics: Statistics
    pp: float
    rank: int
    created_at: datetime
    mode: GameMode
    mode_int: int
    replay: bool

    beatmap: Optional[Beatmap]
    beatmapset: Optional[Beatmapset]
    rank_country: Optional[int]
    rank_global: Optional[int]
    weight: Optional[float]
    user: Optional[UserCompact]
    match: Optional[Match]

@dataclass
class BeatmapUserScore:
    position: int
    score: Score


@dataclass
class CommentableMeta:
    # this class is currently not following the documentation in order to work
    # around https://github.com/ppy/osu-web/issues/7317. Will be updated when
    # that issue is resolved (one way or the other).
    id: Optional[int]
    title: str
    type: Optional[str]
    url: Optional[str]
    # undocumented but still returned,
    owner_id: Optional[int]
    owner_title: Optional[str]

@dataclass
class Comment:
    commentable_id: int
    commentable_type: str
    created_at: datetime
    deleted_at: Optional[datetime]
    edited_at: Optional[datetime]
    edited_by_id: Optional[int]
    id: int
    legacy_name: Optional[str]
    message: Optional[str]
    message_html: Optional[str]
    parent_id: Optional[int]
    pinned: bool
    replies_count: int
    updated_at: datetime
    user_id: int
    votes_count: int

# Cursors are an interesting case. As I understand it, they don't have a
# predefined set of attributes across all endpoints, but instead differ per
# endpoint. I don't want to have dozens of different cursor classes (although
# that would perhaps be the proper way to go about this), so just allow
# any attribute.
# We do, however, have to tell our code what type each attribute is, if we
# receive that atttribute. So ``__annotations`` will need updating as we
# encounter new cursor attributes.
class Cursor(SimpleNamespace):
    __annotations__ = {
        "created_at": datetime,
        "id": int,
        "_id": str,
        "queued_at": str,
        "approved_date": datetime,
        "last_update": str,
        "votes_count": int,
        "page": int
    }

@dataclass
class CommentBundle:
    commentable_meta: List[CommentableMeta]
    comments: List[Comment]
    has_more: bool
    has_more_id: Optional[int]
    included_comments: List[Comment]
    pinned_comments: Optional[List[Comment]]
    sort: str
    top_level_count: Optional[int]
    total: Optional[int]
    user_follow: bool
    user_votes: List[int]
    users: List[UserCompact]
    # undocumented but still returned
    cursor: Cursor


@dataclass
class ForumPost:
    pass

@dataclass
class ForumTopic:
    pass


@dataclass
class ForumTopicAndPosts:
    cursor: Cursor
    search: str
    posts: List[ForumPost]
    topic: ForumTopic

@dataclass
class SearchResult(Generic[T]):
    data: List[T]
    total: int


@dataclass
class WikiPage:
    layout: str
    locale: str
    markdown: str
    path: str
    subtitle: Optional[str]
    tags: List[str]
    title: str

@dataclass
class Search:
    user: Optional[SearchResult[UserCompact]]
    wiki_page: Optional[SearchResult[WikiPage]]

@dataclass
class BeatmapSearchResult:
    beatmapsets: List[Beatmapset]
    cursor: Cursor
    recommended_difficulty: float
    error: Optional[str]
    total: int


# Undocumented Models
# ===================

@dataclass
class BeatmapDiscussionVote:
    # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapDiscussionVote.php#L148
    user_id: int
    score: int

@dataclass
class BeatmapDiscussionPost:
    # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapDiscussionPost.php
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/BeatmapDiscussionPostTransformer.php
    id: int
    beatmap_discussion_id: int
    user_id: Optional[int]
    last_editor_id: Optional[int]
    deleted_by_id: Optional[int]
    system: bool
    message: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    beatmap_discussion: Optional[Any] # Optional[BeatmapDiscussion]

@dataclass
class BeatmapDiscussion:
    # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapDiscussion.php
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/BeatmapDiscussionTransformer.php
    id: int
    beatmapset_id: int
    beatmap_id: Optional[int]
    user_id: Optional[int]
    deleted_by_id: Optional[int]
    # should be ``Optional[int]`` but api returns a string instead
    message_type: Optional[str]
    parent_id: Optional[int]
    # a point of time which is ``timestamp`` milliseconds into the map
    timestamp: Optional[int]
    resolved: bool
    can_be_resolved: bool
    can_grant_kudosu: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    last_post_at: Optional[datetime]
    kudosu_denied: bool
    starting_post: Optional[BeatmapDiscussionPost]
    posts: Optional[List[BeatmapDiscussionPost]]
    beatmap: Optional[BeatmapCompact]
    beatmapset: Optional[BeatmapsetCompact]

# pylint: disable=no-member
BeatmapDiscussionPost.__annotations__["beatmap_discussion"] = Optional[BeatmapDiscussion]
# pylint: enable=no-member

@dataclass
class BeatmapsetDiscussionReview:
    # https://github.com/ppy/osu-web/blob/master/app/Libraries/BeatmapsetDiscussionReview.php
    max_blocks: int

@dataclass
class BeatmapsetEventComment:
    # TODO make this better, everything is optional...
    beatmap_discussion_id: Optional[int]
    beatmap_discussion_post_id: Optional[int]
    new_vote: Optional[BeatmapDiscussionVote]
    votes: Optional[List[BeatmapDiscussionVote]]
    modes: Optional[str]
    # The types change based on event type...
    old: Optional[Any]
    new: Optional[Any]
    reason: Optional[str]

@dataclass
class BeatmapsetEvent:
    # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapsetEvent.php
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/BeatmapsetEventTransformer.php
    beatmapset: Optional[BeatmapsetCompact]
    comment: Optional[BeatmapsetEventComment]
    created_at: Optional[datetime]
    id: int
    # should be ``Optional[int]`` but api returns a string instead
    type: Optional[str]
    user_id: Optional[int]
    discussion: Optional[BeatmapDiscussion]


@dataclass
class ModdingHistoryEventsBundle:
    # https://github.com/ppy/osu-web/blob/master/app/Libraries/ModdingHistoryEventsBundle.php#L84
    events: List[BeatmapsetEvent]
    reviewsConfig: BeatmapsetDiscussionReview
    users: List[UserCompact]
