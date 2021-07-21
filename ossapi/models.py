# opt-in to forward type annotations
# https://docs.python.org/3.7/whatsnew/3.7.html#pep-563-postponed-evaluation-of-annotations
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TypeVar, Generic, Any, List
from types import SimpleNamespace

from ossapi.mod import Mod
from ossapi.enums import (UserAccountHistory, ProfileBanner, UserBadge, Country,
    Cover, UserGroup, UserMonthlyPlaycount, UserPage, UserReplaysWatchedCount,
    UserAchievement, UserProfileCustomization, RankHistory, Kudosu, PlayStyles,
    ProfilePage, GameMode, RankStatus, Failtimes, Covers, Hype, Availability,
    Nominations, Statistics, Grade, Weight, MessageType, KudosuAction,
    KudosuGiver, KudosuPost, EventType, EventAchivement, EventUser,
    EventBeatmap, BeatmapsetApproval, EventBeatmapset, KudosuVote,
    BeatmapsetEventType, UserRelationType, UserLevel, UserGradeCounts,
    GithubUser, ChangelogSearch)
from ossapi.utils import Datetime, Model

T = TypeVar("T")
S = TypeVar("S")
# if there are no more results, a null cursor is returned instead.
# So always let the cursor be nullable to catch this. It's the user's
# responsibility to check for a null cursor to see if there are any more
# results.
CursorT = Optional["Cursor"]

"""
a type hint of ``Optional[Any]`` or ``Any`` means that I don't know what type it
is, not that the api actually lets any type be returned there.
"""

# =================
# Documented Models
# =================

@dataclass
class UserCompact(Model):
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
    last_visit: Optional[Datetime]
    pm_friends_only: bool
    # TODO pretty sure this needs to be optional but it's not documented as
    # such, open an issue?
    profile_colour: Optional[str]
    username: str

    # optional fields
    # ---------------
    account_history: Optional[List[UserAccountHistory]]
    active_tournament_banner: Optional[ProfileBanner]
    badges: Optional[List[UserBadge]]
    beatmap_playcounts_count: Optional[int]
    blocks: Optional[UserRelation]
    country: Optional[Country]
    cover: Optional[Cover]
    favourite_beatmapset_count: Optional[int]
    # undocumented
    follow_user_mapping: Optional[List[int]]
    follower_count: Optional[int]
    friends: Optional[List[UserRelation]]
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
    # undocumented
    mapping_follower_count: Optional[int]
    monthly_playcounts: Optional[List[UserMonthlyPlaycount]]
    page: Optional[UserPage]
    previous_usernames: Optional[List[str]]
    # deprecated, replaced by ranked_beatmapset_count
    ranked_and_approved_beatmapset_count: Optional[int]
    ranked_beatmapset_count: Optional[int]
    replays_watched_counts: Optional[List[UserReplaysWatchedCount]]
    scores_best_count: Optional[int]
    scores_first_count: Optional[int]
    scores_recent_count: Optional[int]
    statistics: Optional[UserStatistics]
    statistics_rulesets: Optional[UserStatisticsRulesets]
    support_level: Optional[int]
    # deprecated, replaced by pending_beatmapset_count
    unranked_beatmapset_count: Optional[int]
    pending_beatmapset_count: Optional[int]
    unread_pm_count: Optional[int]
    user_achievements: Optional[List[UserAchievement]]
    user_preferences: Optional[UserProfileCustomization]
    rank_history: Optional[RankHistory]
    # deprecated, replaced by rank_history
    rankHistory: Optional[RankHistory]

@dataclass
class User(UserCompact):
    comments_count: int
    cover_url: str
    discord: Optional[str]
    has_supported: bool
    interests: Optional[str]
    join_date: Datetime
    kudosu: Kudosu
    location: Optional[str]
    max_blocks: int
    max_friends: int
    occupation: Optional[str]
    playmode: str
    playstyle: Optional[PlayStyles]
    post_count: int
    profile_order: List[ProfilePage]
    title: Optional[str]
    title_url: Optional[str]
    twitter: Optional[str]
    website: Optional[str]



@dataclass
class BeatmapCompact(Model):
    # required fields
    # ---------------
    difficulty_rating: float
    id: int
    mode: GameMode
    status: RankStatus
    total_length: int
    version: str
    user_id: int

    # optional fields
    # ---------------
    beatmapset: Optional[BeatmapsetCompact]
    checksum: Optional[str]
    failtimes: Optional[Failtimes]
    max_combo: Optional[int]


@dataclass
class Beatmap(BeatmapCompact):
    total_length: int
    version: str
    accuracy: float
    ar: float
    beatmapset_id: int
    bpm: float
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    deleted_at: Optional[Datetime]
    drain: float
    hit_length: int
    is_scoreable: bool
    last_updated: Datetime
    mode_int: int
    passcount: int
    playcount: int
    ranked: RankStatus
    url: str

    # overridden fields
    # -----------------
    beatmapset: Optional[Beatmapset]


@dataclass
class BeatmapsetCompact(Model):
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
    # documented as being a str, docs should say this is a bool
    video: bool
    nsfw: bool
    # documented as being in ``Beatmapset`` only, but returned by
    # ``api.beatmapset_events`` which uses a ``BeatmapsetCompact``.
    hype: Optional[Hype]

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
    bpm: float
    can_be_hyped: bool
    discussion_enabled: bool
    discussion_locked: bool
    is_scoreable: bool
    last_updated: Datetime
    legacy_thread_url: Optional[str]
    nominations_summary: Nominations
    ranked: RankStatus
    ranked_date: Optional[Datetime]
    storyboard: bool
    submitted_date: Optional[Datetime]
    tags: str


@dataclass
class Match(Model):
    pass

@dataclass
class Score(Model):
    """
    https://osu.ppy.sh/docs/index.html#score
    """
    id: int
    # documented as non-optional in docs
    best_id: Optional[int]
    user_id: int
    accuracy: float
    mods: Mod
    score: int
    max_combo: int
    perfect: bool
    statistics: Statistics
    # documented as non-optional in docs but broken beatmaps like acid rain
    # (1981090) have scores with null pp values. TODO open issue
    pp: Optional[float]
    rank: Grade
    created_at: Datetime
    mode: GameMode
    mode_int: int
    replay: bool
    passed: bool

    beatmap: Optional[Beatmap]
    beatmapset: Optional[BeatmapsetCompact]
    rank_country: Optional[int]
    rank_global: Optional[int]
    weight: Optional[Weight]
    user: Optional[UserCompact]
    match: Optional[Match]

@dataclass
class BeatmapUserScore(Model):
    position: int
    score: Score

@dataclass
class BeatmapScores(Model):
    scores: List[Score]
    userScore: Optional[BeatmapUserScore]


@dataclass
class CommentableMeta(Model):
    # this class is currently not following the documentation in order to work
    # around https://github.com/ppy/osu-web/issues/7317. Will be updated when
    # that issue is resolved (one way or the other).
    id: Optional[int]
    title: str
    type: Optional[str]
    url: Optional[str]
    # both undocumented
    owner_id: Optional[int]
    owner_title: Optional[str]

@dataclass
class Comment(Model):
    commentable_id: int
    commentable_type: str
    created_at: Datetime
    deleted_at: Optional[Datetime]
    edited_at: Optional[Datetime]
    edited_by_id: Optional[int]
    id: int
    legacy_name: Optional[str]
    message: Optional[str]
    message_html: Optional[str]
    parent_id: Optional[int]
    pinned: bool
    replies_count: int
    updated_at: Datetime
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
class Cursor(SimpleNamespace, Model):
    __annotations__ = {
        "created_at": Datetime,
        "id": int,
        "_id": str,
        "queued_at": str,
        "approved_date": Datetime,
        "last_update": str,
        "votes_count": int,
        "page": int,
        "limit": int,
        "_score": float
    }

@dataclass
class CommentBundle(Model):
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
    # undocumented
    cursor: CursorT


@dataclass
class ForumPost(Model):
    pass

@dataclass
class ForumTopic(Model):
    pass


@dataclass
class ForumTopicAndPosts(Model):
    cursor: CursorT
    search: str
    posts: List[ForumPost]
    topic: ForumTopic

@dataclass
class SearchResult(Generic[T], Model):
    data: List[T]
    total: int


@dataclass
class WikiPage(Model):
    layout: str
    locale: str
    markdown: str
    path: str
    subtitle: Optional[str]
    tags: List[str]
    title: str
    available_locales: List[str]

@dataclass
class Search(Model):
    user: Optional[SearchResult[UserCompact]]
    wiki_page: Optional[SearchResult[WikiPage]]

@dataclass
class Spotlight(Model):
    end_date: Datetime
    id: int
    mode_specific: bool
    participant_count: Optional[int]
    name: str
    start_date: Datetime
    type: str

@dataclass
class Spotlights(Model):
    spotlights: List[Spotlight]

@dataclass
class Rankings(Model):
    beatmapsets: Optional[List[Beatmapset]]
    cursor: CursorT
    ranking: List[UserStatistics]
    spotlight: Optional[Spotlight]
    total: int

@dataclass
class BeatmapsetDiscussionPost(Model):
    id: int
    beatmapset_discussion_id: int
    user_id: int
    # documented as non-optional
    last_editor_id: Optional[int]
    # documented as non-optional
    deleted_by_id: Optional[int]
    system: bool
    message: str
    created_at: Datetime
    updated_at: Datetime
    deleted_at: Optional[Datetime]

@dataclass
class BeatmapsetDiscussion(Model):
    id: int
    beatmapset_id: int
    # documented as non-optional
    beatmap_id: Optional[int]
    user_id: int
    # documented as non-optional
    deleted_by_id: Optional[int]
    message_type: MessageType
    parent_id: Optional[int]
    # a point of time which is ``timestamp`` milliseconds into the map
    timestamp: Optional[int]
    resolved: bool
    can_be_resolved: bool
    can_grant_kudosu: bool
    created_at: Datetime
    updated_at: Datetime
    deleted_at: Optional[Datetime]
    # documented as non-optional
    last_post_at: Optional[Datetime]
    kudosu_denied: bool
    # documented as non-optional
    starting_post: Optional[BeatmapsetDiscussionPost]
    # documented as non-optional
    posts: Optional[List[BeatmapsetDiscussionPost]]
    beatmap: Optional[BeatmapCompact]
    beatmapset: Optional[BeatmapsetCompact]

@dataclass
class BeatmapsetDiscussionVote(Model):
    score: int
    user_id: int

    # all of the following are documented as being returned, but they never are
    # (for the endpoints we've implemented anyway)
    # beatmapset_discussion_id: int
    # created_at: Datetime
    # id: int
    # updated_at: Datetime

@dataclass
class KudosuHistory(Model):
    id: int
    action: KudosuAction
    amount: int
    # TODO enumify this. Described as "Object type which the exchange happened
    # on (forum_post, etc)." in https://osu.ppy.sh/docs/index.html#kudosuhistory
    model: str
    created_at: Datetime
    giver: Optional[KudosuGiver]
    post: KudosuPost
    # TODO type hint properly when https://github.com/ppy/osu-web/issues/7549 is
    # resolved
    details: Any

@dataclass
class BeatmapPlaycount(Model):
    beatmap_id: int
    beatmap: Optional[BeatmapCompact]
    beatmapset: Optional[BeatmapsetCompact]
    count: int


# we use this class to determine which event dataclass to instantiate and
# return, based on the value of the ``type`` parameter.
class _Event(Model):
    @classmethod
    def override_class(cls, data):
        mapping = {
            EventType.ACHIEVEMENT: AchievementEvent,
            EventType.BEATMAP_PLAYCOUNT: BeatmapPlaycountEvent,
            EventType.BEATMAPSET_APPROVE: BeatmapsetApproveEvent,
            EventType.BEATMAPSET_DELETE: BeatmapsetDeleteEvent,
            EventType.BEATMAPSET_REVIVE: BeatmapsetReviveEvent,
            EventType.BEATMAPSET_UPDATE: BeatmapsetUpdateEvent,
            EventType.BEATMAPSET_UPLOAD: BeatmapsetUploadEvent,
            EventType.RANK: RankEvent,
            EventType.RANK_LOST: RankLostEvent,
            EventType.USER_SUPPORT_FIRST: UserSupportFirstEvent,
            EventType.USER_SUPPORT_AGAIN: UserSupportAgainEvent,
            EventType.USER_SUPPORT_GIFT: UserSupportGiftEvent,
            EventType.USERNAME_CHANGE: UsernameChangeEvent
        }
        type_ = EventType(data["type"])
        return mapping[type_]

@dataclass
class Event(Model):
    created_at: Datetime
    createdAt: Datetime
    id: int
    type: EventType

@dataclass
class AchievementEvent(Event):
    achievement: EventAchivement
    user: EventUser

@dataclass
class BeatmapPlaycountEvent(Event):
    beatmap: EventBeatmap
    count: int

@dataclass
class BeatmapsetApproveEvent(Event):
    approval: BeatmapsetApproval
    beatmapset: EventBeatmapset
    user: EventUser

@dataclass
class BeatmapsetDeleteEvent(Event):
    beatmapset: EventBeatmapset

@dataclass
class BeatmapsetReviveEvent(Event):
    beatmapset: EventBeatmapset
    user: EventUser

@dataclass
class BeatmapsetUpdateEvent(Event):
    beatmapset: EventBeatmapset
    user: EventUser

@dataclass
class BeatmapsetUploadEvent(Event):
    beatmapset: EventBeatmapset
    user: EventUser

@dataclass
class RankEvent(Event):
    scoreRank: str
    rank: int
    mode: GameMode
    beatmap: EventBeatmap
    user: EventUser

@dataclass
class RankLostEvent(Event):
    mode: GameMode
    beatmap: EventBeatmap
    user: EventUser

@dataclass
class UserSupportFirstEvent(Event):
    user: EventUser

@dataclass
class UserSupportAgainEvent(Event):
    user: EventUser

@dataclass
class UserSupportGiftEvent(Event):
    beatmap: EventBeatmap

@dataclass
class UsernameChangeEvent(Event):
    user: EventUser

@dataclass
class Build(Model):
    created_at: Datetime
    display_version: str
    id: int
    update_stream: Optional[UpdateStream]
    users: int
    version: Optional[str]
    changelog_entries: Optional[List[ChangelogEntry]]
    versions: Optional[Versions]

@dataclass
class Versions(Model):
    next: Optional[Build]
    previous: Optional[Build]

@dataclass
class UpdateStream(Model):
    display_name: Optional[str]
    id: int
    is_featured: bool
    name: str
    latest_build: Optional[Build]
    user_count: Optional[int]

@dataclass
class ChangelogEntry(Model):
    category: str
    created_at: Optional[Datetime]
    github_pull_request_id: Optional[int]
    github_url: Optional[str]
    id: Optional[int]
    major: bool
    message_html: Optional[str]
    repository: Optional[str]
    title: Optional[str]
    type: str
    url: Optional[str]
    github_user: GithubUser

@dataclass
class ChangelogListing(Model):
    builds: List[Build]
    search: ChangelogSearch
    streams: List[UpdateStream]

# ===================
# Undocumented Models
# ===================

@dataclass
class BeatmapSearchResult(Model):
    beatmapsets: List[Beatmapset]
    cursor: CursorT
    recommended_difficulty: float
    error: Optional[str]
    total: int
    search: Any

@dataclass
class BeatmapsetDiscussionReview(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Libraries/BeatmapsetDiscussionReview.php
    max_blocks: int

@dataclass
class BeatmapsetDiscussionPostResult(Model):
    # This is for the ``/beatmapsets/discussions/posts`` endpoint because
    # the actual return type of that endpoint doesn't match the docs at
    # https://osu.ppy.sh/docs/index.html#get-beatmapset-discussion-posts. TODO
    # open issue?
    beatmapsets: List[BeatmapsetCompact]
    discussions: List[BeatmapsetDiscussion]
    cursor: CursorT
    posts: List[BeatmapsetDiscussionPost]
    users: List[UserCompact]

@dataclass
class BeatmapsetEventComment(Model):
    beatmap_discussion_id: int
    beatmap_discussion_post_id: int

@dataclass
class BeatmapsetEventCommentNoPost(Model):
    beatmap_discussion_id: int
    beatmap_discussion_post_id: None

@dataclass
class BeatmapsetEventCommentNone(Model):
    beatmap_discussion_id: None
    beatmap_discussion_post_id: None


@dataclass
class BeatmapsetEventCommentChange(Generic[S], BeatmapsetEventCommentNone):
    old: S
    new: S

@dataclass
class BeatmapsetEventCommentLovedRemoval(BeatmapsetEventCommentNone):
    reason: str

@dataclass
class BeatmapsetEventCommentKudosuChange(BeatmapsetEventCommentNoPost):
    new_vote: KudosuVote
    votes: List[KudosuVote]

@dataclass
class BeatmapsetEventCommentKudosuRecalculate(BeatmapsetEventCommentNoPost):
    new_vote: Optional[KudosuVote]

@dataclass
class BeatmapsetEventCommentOwnerChange(BeatmapsetEventCommentNone):
    beatmap_id: int
    beatmap_version: str
    new_user_id: int
    new_user_username: str

@dataclass
class BeatmapsetEventCommentNominate(Model):
    # for some reason this comment type doesn't have the normal
    # beatmap_discussion_id and beatmap_discussion_post_id attributes (they're
    # not even null, just missing). TODO Open an issue on osu-web?
    modes: List[GameMode]

@dataclass
class BeatmapsetEvent(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapsetEvent.php
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/BeatmapsetEventTransformer.php
    id: int
    type: BeatmapsetEventType
    comment: str
    created_at: Datetime

    user_id: Optional[int]
    beatmapset: Optional[BeatmapsetCompact]
    discussion: Optional[BeatmapsetDiscussion]

    def override_types(self):
        mapping = {
            BeatmapsetEventType.BEATMAP_OWNER_CHANGE: BeatmapsetEventCommentOwnerChange,
            BeatmapsetEventType.DISCUSSION_DELETE: BeatmapsetEventCommentNoPost,
            # TODO: ``api.beatmapsets_events(types=[BeatmapsetEventType.DISCUSSION_LOCK])``
            # doesn't seem to be recognized, just returns all events. Was this
            # type discontinued?
            # BeatmapsetEventType.DISCUSSION_LOCK: BeatmapsetEventComment,
            BeatmapsetEventType.DISCUSSION_POST_DELETE: BeatmapsetEventComment,
            BeatmapsetEventType.DISCUSSION_POST_RESTORE: BeatmapsetEventComment,
            BeatmapsetEventType.DISCUSSION_RESTORE: BeatmapsetEventCommentNoPost,
            # same here
            # BeatmapsetEventType.DISCUSSION_UNLOCK: BeatmapsetEventComment,
            BeatmapsetEventType.DISQUALIFY: BeatmapsetEventComment,
            # same here
            # BeatmapsetEventType.DISQUALIFY_LEGACY: BeatmapsetEventComment
            BeatmapsetEventType.GENRE_EDIT: BeatmapsetEventCommentChange[str],
            BeatmapsetEventType.ISSUE_REOPEN: BeatmapsetEventComment,
            BeatmapsetEventType.ISSUE_RESOLVE: BeatmapsetEventComment,
            BeatmapsetEventType.KUDOSU_ALLOW: BeatmapsetEventCommentNoPost,
            BeatmapsetEventType.KUDOSU_DENY: BeatmapsetEventCommentNoPost,
            BeatmapsetEventType.KUDOSU_GAIN: BeatmapsetEventCommentKudosuChange,
            BeatmapsetEventType.KUDOSU_LOST: BeatmapsetEventCommentKudosuChange,
            BeatmapsetEventType.KUDOSU_RECALCULATE: BeatmapsetEventCommentKudosuRecalculate,
            BeatmapsetEventType.LANGUAGE_EDIT: BeatmapsetEventCommentChange[str],
            BeatmapsetEventType.LOVE: type(None),
            BeatmapsetEventType.NOMINATE: BeatmapsetEventCommentNominate,
            # same here
            # BeatmapsetEventType.NOMINATE_MODES: BeatmapsetEventComment,
            BeatmapsetEventType.NOMINATION_RESET: BeatmapsetEventComment,
            BeatmapsetEventType.QUALIFY: type(None),
            BeatmapsetEventType.RANK: type(None),
            BeatmapsetEventType.REMOVE_FROM_LOVED: BeatmapsetEventCommentLovedRemoval,
            BeatmapsetEventType.NSFW_TOGGLE: BeatmapsetEventCommentChange[bool],
        }
        type_ = BeatmapsetEventType(self.type)
        return {"comment": mapping[type_]}



@dataclass
class ModdingHistoryEventsBundle(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Libraries/ModdingHistoryEventsBundle.php#L84
    events: List[BeatmapsetEvent]
    reviewsConfig: BeatmapsetDiscussionReview
    users: List[UserCompact]

@dataclass
class UserRelation(Model):
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserRelationTransformer.php#L16
    target_id: int
    relation_type: UserRelationType
    mutual: bool

    # optional fields
    # ---------------
    target: Optional[UserCompact]


@dataclass
class UserStatistics(Model):
    # undocumented
    level: UserLevel
    pp: float
    ranked_score: int
    hit_accuracy: float
    play_count: int
    play_time: int
    total_score: int
    total_hits: int
    maximum_combo: int
    replays_watched_by_others: int
    is_ranked: bool
    grade_counts: UserGradeCounts

    # optional fields
    # ---------------
    country_rank: Optional[int]
    global_rank: Optional[int]
    rank: Optional[Any]
    user: Optional[UserCompact]
    variants: Optional[Any]

@dataclass
class UserStatisticsRulesets(Model):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserStatisticsRulesetsTransformer.php
    osu: Optional[UserStatistics]
    taiko: Optional[UserStatistics]
    fruits: Optional[UserStatistics]
    mania: Optional[UserStatistics]
