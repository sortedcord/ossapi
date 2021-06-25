[![PyPI version](https://badge.fury.io/py/ossapi.svg)](https://pypi.org/project/ossapi/)

# ossapi

ossapi is a python wrapper for the osu! api. ossapi supports both [api v2](https://osu.ppy.sh/docs/index.html) and [api v1](https://github.com/ppy/osu-api/wiki). See [API v2 Usage](#api-v2-usage) for api v2 documentation, or [API v1 Usage](#api-v1-usage) for api v1 documentation.

To install ossapi for api v2, which is currently in beta:

```bash
pip install --pre ossapi
```

To upgrade ossapi for api v2:

```bash
pip install --pre -U ossapi
```

To install ossapi for api v1:

```bash
pip install ossapi
```

## API v2 Usage

Note that api v2 requires python 3.8+.

### Authenticating

The osu api provides two ways to authenticate, [authorization code](https://oauth.net/2/grant-types/authorization-code/) and [client credentials](https://oauth.net/2/grant-types/client-credentials/). Authorization code grants full access to the api, but requires user interaction to authenticate the first time. Client credentials grants guest user access only, but authenticates automatically.

In either case you will need to create on oauth client on [your settings page](https://osu.ppy.sh/home/account/edit). Give it whatever name you want. However, your callback url \*must* be a port on localhost. So `http://localhost:3914/`, `http://localhost:727/`, etc are all acceptable values. Make sure you're not taking a commonly used port.

#### Authorization Code

With the authorization code flow we will use the oauth client's id, secret, and redirect_uri to authenticate. Copy these values from the oauth application you just created.

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
print(api.search_beatmaps(query="the big black").beatmapsets[0].title)
print(api.beatmapsets_events(types=[BeatmapsetEventType.ISSUE_REOPEN]).events[0].type)
print(api.user(12092800).playstyle)
print(api.wiki_page("en", "Welcome").available_locales)
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

## API v1 Usage

```python
from ossapi import Ossapi

api = Ossapi("API_KEY")
json = api.get_replay({"m": "0", "b": "1776628", "u": "3256299"})
# either strings or ints will work. Returns something like
# `{"content":"XQAAIA....3fISw=","encoding":"base64"}`
```
