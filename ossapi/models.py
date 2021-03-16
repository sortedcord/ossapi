from dataclasses import dataclass
from typing import Optional, TypeVar, Generic
from datetime import datetime
from enum import Enum
from types import SimpleNamespace

from ossapi.mod import Mod

class ProfilePage(Enum):
    ME = "me"
    RECENT_ACTIVITY = "recent_activity"
    BEATMAPS = "beatmaps"
    HISTORICAL = "historical"
    KUDOSU = "kudosu"
    TOP_RANKS = "top_ranks"
    MEDALS = "medals"


T = TypeVar("T")



@dataclass
class Beatmap:
    difficulty_rating: int
    id: int
    mode: str
    status: str
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

@dataclass
class Beatmapset:
    artist: str
    artist_unicode: str
    covers: dict[str, str]
    creator: str
    favourite_count: int
    # TODO figure out type
    hype: int
    id: int
    nsfw: bool
    play_count: int
    preview_url: str
    source: str
    status: str
    title: str
    title_unicode: str
    user_id: int
    video: bool
    availability: dict[str, Optional[bool]]
    bpm: int
    can_be_hyped: bool
    discussion_enabled: bool
    discussion_locked: bool
    is_scoreable: bool
    last_updated: datetime
    legacy_thread_url: str
    nominations_summary: dict[str, int]
    ranked: int
    ranked_date: datetime
    storyboard: bool
    submitted_date: datetime
    tags: str
    ratings: list[int]
    beatmaps: Optional[Beatmap]



@dataclass
class BeatmapExtended(Beatmap):
    """
    attributes returned by https://osu.ppy.sh/docs/index.html#get-beatmap in
    addition to a regular ``Beatmap``.
    """
    beatmapset: Beatmapset
    failtimes: dict[str, list[int]]
    max_combo: int

@dataclass
class Statistics:
    count_50: int
    count_100: int
    count_300: int
    count_geki: int
    count_katu: int
    count_miss: int

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
class UserCompact:
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


@dataclass
class User(UserCompact):
    cover_url: str
    discord: Optional[str]
    has_supported: bool
    interests: Optional[str]
    join_date: datetime
    # TODO
    kudosu: None
    location: Optional[str]
    max_blocks: int
    max_friends: int
    occupation: Optional[str]
    playmode: str
    playstyle: list[str]
    post_count: int
    profile_order: list[ProfilePage]
    title: Optional[str]
    twitter: Optional[str]
    website: Optional[str]
    country: Country
    cover: Cover
    is_admin: bool
    is_bng: bool
    is_full_bng: bool
    is_gmt: bool
    is_limited_bn: bool
    is_moderator: bool
    is_nat: bool
    is_restricted: bool
    is_silenced: bool
    groups: list[str]


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
    mode: str
    mode_int: int
    replay: bool

    beatmap: Optional[Beatmap]
    beatmapset: Optional[Beatmapset]
    rank_country: Optional[int]
    rank_global: Optional[int]
    weight: Optional[float]
    user: Optional[User]
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
    commentable_meta: list[CommentableMeta]
    comments: list[Comment]
    has_more: bool
    has_more_id: Optional[int]
    included_comments: list[Comment]
    pinned_comments: Optional[list[Comment]]
    sort: str
    top_level_count: Optional[int]
    total: Optional[int]
    user_follow: bool
    user_votes: list[int]
    users: list[UserCompact]
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
    posts: list[ForumPost]
    topic: ForumTopic

@dataclass
class SearchResult(Generic[T]):
    data: list[T]
    total: int


@dataclass
class WikiPage:
    layout: str
    locale: str
    markdown: str
    path: str
    subtitle: Optional[str]
    tags: list[str]
    title: str

@dataclass
class Search:
    user: Optional[SearchResult[UserCompact]]
    wiki_page: Optional[SearchResult[WikiPage]]


@dataclass
class BeatmapSearchResult:
    beatmapsets: list[Beatmapset]
    cursor: Cursor
    recommended_difficulty: float
    error: Optional[str]
    total: int
# 'cursor': {'approved_date': '1615570940000', '_id': '1385279'}, 'recommended_difficulty': 6.106446268384076, 'error': None, 'total': 27056}


# the get replay endpoint
# (https://osu.ppy.sh/docs/index.html#apiv2scoresmodescore) has some weird
# return values, and since it's not documented we're just going to hackily work
# around them for now.

@dataclass
class ReplayBeatmap(Beatmap):
    max_combo: int

@dataclass
class ReplayScore(Score):
    beatmap: ReplayBeatmap
