from dataclasses import dataclass
from typing import Optional, TypeVar, Generic
from datetime import datetime

T = TypeVar("T")


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
class Score:
    """
    https://osu.ppy.sh/docs/index.html#score
    """
    id: int
    best_id: int
    user_id: int
    accuracy: float
    mods: list[str]
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

    beatmap: Optional[Beatmap] = None
    beatmapset: Optional[None] = None
    rank_country: Optional[int] = None
    rank_global: Optional[int] = None
    weight: Optional[float] = None
    user: Optional[None] = None
    match: Optional[None] = None

@dataclass
class BeatmapUserScore:
    position: int
    score: Score

@dataclass
class CommentBundle:
    pass

@dataclass
class ForumPost:
    pass

@dataclass
class ForumTopic:
    pass

@dataclass
class Cursor:
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
class WikiPage:
    pass

@dataclass
class Search:
    user: Optional[SearchResult[UserCompact]] = None
    wiki_page: Optional[SearchResult[WikiPage]] = None

model_types = (Beatmap, Beatmapset, BeatmapUserScore, Score, Statistics,
    CommentBundle, ForumPost, ForumTopic, ForumTopicAndPosts, Cursor,
    SearchResult, UserCompact, WikiPage, Search, BeatmapExtended)
