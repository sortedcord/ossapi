[![PyPI version](https://badge.fury.io/py/ossapi.svg)](https://pypi.org/project/ossapi/)

# ossapi

ossapi is a python wrapper for the osu! api. ossapi supports both [api v2](https://osu.ppy.sh/docs/index.html) and [api v1](https://github.com/ppy/osu-api/wiki). See [API v2 Usage](#api-v2-usage) for api v2 documentation, or [API v1 Usage](#api-v1-usage) for api v1 documentation.

To install:

```bash
pip install ossapi
```

To upgrade:

```bash
pip install -U ossapi
```

## API v2 Usage

Please note that api v2 requires python 3.8+ (api v1 only requires python 3.6+).

### Authenticating

The osu api provides two ways to authenticate, [authorization code](https://oauth.net/2/grant-types/authorization-code/) and [client credentials](https://oauth.net/2/grant-types/client-credentials/). Authorization code grants full access to the api, but requires user interaction to authenticate the first time. Client credentials grants guest user access only, but authenticates automatically.

In either case you will need to create on oauth client on [your settings page](https://osu.ppy.sh/home/account/edit). Give it whatever name you want. However, your callback url \*must* be a port on localhost. So `http://localhost:3914/`, `http://localhost:727/`, etc are all acceptable values. Make sure you're not taking a commonly used port.

#### Authorization Code

With the authorization code flow we will use the oauth client's id, secret, and redirect_uri (aka callback url) to authenticate. Copy these values from the oauth application you just created.

```python
from ossapi import *
api = OssapiV2(client_id, client_secret, redirect_uri)
```

The first time you run this code, a page will open in your browser asking you to authenticate with osu! for your client. Once you do so, we cache the response, so you can use ossapi in the future without needing to re-authenticate.

As stated above, this flow grants full access to the api through your user.

#### Client Credentials

With the client credentials flow we will use the oauth client's id and secret to authenticate. Copy these values from the oauth application you just created.

```python
from ossapi import *
api = OssapiV2(client_id, client_secret)
```

Unlike the authorization code flow, this authentication happens automatically and silently, and does not require user intervention. This is ideal for scripts which need to run without user interaction. As stated above however, this flow grants only guest user access to the api. This means you will not be able to use certain endpoints, like downloading replays.

### Supported Endpoints

Here is a complete list of endpoints we currently have implemented. You can track our progress towards implementing all documented api v2 endpoints here: <https://github.com/circleguard/ossapi/issues/14>.

```python
print(api.beatmapset_discussion_posts().discussions[0].message_type)
print(api.user_recent_activity(10690090)[0].created_at)
print(api.spotlights()[0].name)
print(api.user_beatmaps(user_id=12092800, type_="most_played")[0].count)
print(api.user_kudosu(user_id=3178418)[0].action)
print(api.beatmap_scores(beatmap_id=1981090).scores[0].id)
print(api.beatmap(beatmap_id=1981090).max_combo)
print(api.ranking("osu", RankingType.PERFORMANCE, country="US").ranking[0].user.username)
print(api.user_scores(12092800, "best")[0].accuracy)
print(api.beatmap(beatmap_id=221777).last_updated)
print(api.beatmap_user_score(beatmap_id=221777, user_id=2757689).score.mods)
print(api.search(query="peppy").user.data[0].profile_colour)
print(api.comment(comment_id=1).comments[0].message)
print(api.download_score(mode="osu", score_id=2797309065))
print(api.search_beatmapsets(query="the big black").beatmapsets[0].title)
print(api.beatmapsets_events(types=[BeatmapsetEventType.ISSUE_REOPEN]).events[0].type)
print(api.user(12092800).playstyle)
print(api.wiki_page("en", "Welcome").available_locales)
print(api.changelog_build("stable40", "20210520.2").users)
print(api.changelog_listing().builds[0].display_version)
print(api.changelog_lookup("lazer").changelog_entries[0].github_pull_request_id)
print(api.forum_topic(141240).posts[0].forum_id)
print(api.beatmapset_discussion_votes().votes[0].score)
print(api.score(mode="osu", score_id=2797309065).accuracy)
```

Note that although this code just prints a single attribute for each endpoint, you can obviously do more complicated things like iterate over arrays:

```python
response = api.ranking("osu", RankingType.PERFORMANCE, country="US")
for ranking in response.ranking:
    print(f"global #{ranking.global_rank}: {ranking.user.username}")
```

### Pagination

Some endpoints are paginated, and so you may need a way to access the 3rd, 5th, or 25th page of the results. The way to do this is with the `Cursor` class.

For example, the `/rankings/` endpoint is paginated. If we wanted to get the top 1-50 players, we don't need a cursor at all, since paginated endpoints return the first page by default:

```python
r = api.ranking("osu", RankingType.PERFORMANCE)
print(r.ranking[-1].global_rank) # 50
```

Accessing the subsequent page of results immediately afterwards is such a common use case that all paginated endpoints return a `cursor` attribute which is already pre-prepared to retrive the next page. Just pass it to a new api call:

```python
r = api.ranking("osu", RankingType.PERFORMANCE)
cursor = r.cursor
print(r.ranking[-1].global_rank) # 50

r = api.ranking("osu", RankingType.PERFORMANCE, cursor=cursor)
print(r.ranking[-1].global_rank) # 100
```

However, this doesn't work so well if you want to skip a bunch of pages and go straight to eg the 20th page. To do so, construct your own `Cursor` object and use that:

```python
cursor = Cursor(page=20)
r = api.ranking("osu", RankingType.PERFORMANCE, cursor=cursor)
print(r.ranking[-1].global_rank) # 1000
```

If there are no more pages, the `cursor` object of the response will be `None`:

```python
cursor = Cursor(page=199)
r = api.ranking("osu", RankingType.PERFORMANCE, cursor=cursor)
print(r.cursor) # Cursor(page=200)

cursor = Cursor(page=200) # there are only 200 rankings pages
r = api.ranking("osu", RankingType.PERFORMANCE, cursor=cursor)
print(r.cursor) # None
```

### Advanced Usage

#### User and Beatmap as parameters

Some functions, like `api.beatmap_scores`, take a beatmap_id (or user_id). We also allow passing a `Beatmap` / `BeatmapCompact` (or `User` / `UserCompact`) in place of the id as a convenience:

```python
beatmap = api.beatmap(221777)
assert api.beatmap_scores(beatmap) == api.beatmap_scores(beatmap.id)
```

Internally, we simply take `beatmap.id` (or `user.id`) and supply that to the function.

#### Expandable Models

`UserCompact` and `BeatmapCompact` classes are "expandable" into `User` and `Beatmap` respectively. Some endpoints only return eg a `UserCompact`, but you may want attributes that are present on `User`. To expand such a class, call `#expand`:

```python
compact_user = api.search(query="tybug").user.data[0]
# `statistics` is only available on `User` not `UserCompact`,
# so expansion is necessary
print(compact_user.expand().statistics.ranked_score)
# this is equivalent to
print(api.user(compact_user).statistics.ranked_score)
```

Similarly, `beatmap = compact_beatmap.expand()` is equivalent to `beatmap = api.beatmap(compact_beatmap)`.

(Note that beatmapsets will also be expandable in the future; I am waiting for the beatmapset lookup endpoint to become documented first.)

## API v1 Usage

You can get your api v1 key at <https://osu.ppy.sh/p/api/>. Note that due to a [redirection bug](https://github.com/ppy/osu-web/issues/2867), you may need to log in and wait 30 seconds before being able to access the api page through the above link.

Basic usage:

```python
from ossapi import Ossapi

api = Ossapi("key")
print(api.get_beatmaps(user=10690090)[0].submit_date)
print(api.get_match(69063884).games[0].game_id)
print(api.get_scores(221777)[0].username)
print(len(api.get_replay(beatmap_id=221777, user=6974470)))
print(api.get_user(12092800).playcount)
print(api.get_user_best(12092800)[0].pp)
print(api.get_user_recent(12092800)[0].beatmap_id)
```

For convenience when working with mods, we provide a Mod class, which is used wherever the api returns a mod value. An overview of its methods, in example format:

```python
from ossapi import Mod, Ossapi

api = Ossapi("key")

mods = api.get_scores(221777)[0].mods
# Mod's __str__ uses short_name()
print(mods)
print(mods.short_name())

# to break down a mod into its component mods (eg if you want ["HD", "DT"] from "HDDT")
print(mods.decompose())

# to get the long form name (HD -> Hidden)
print(mods.long_name())

# to access the underlying value
print(mods.value)

# to add or remove a mod from the mod combination, use + and -
print(mods + Mod.FL)
print(mods - Mod.HD)
# you can also add or remove multiple mods at a time
print(mods - Mod.HDHR)

# common mod combinations are stored as static variables under `Mod` for convenience
print(Mod.HDDT, Mod.HDHR, Mod.HDDTHR)
# otherwise, the preferred way to build up mods is by adding them together
print(Mod.HD + Mod.FL + Mod.EZ)
# alternatively, you can instantiate with the raw value
print(Mod(1034))
assert Mod.HD + Mod.FL + Mod.EZ == Mod(1034)
```
