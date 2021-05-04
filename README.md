[![PyPI version](https://badge.fury.io/py/ossapi.svg)](https://pypi.org/project/ossapi/)

# ossapi

ossapi (so called to avoid pypi naming conflicts with the existing osuapi) is a python wrapper for the osu! api. Ossapi includes support for api v2.

## Usage

To install:

```bash
pip install ossapi
```

To use:

```python
from ossapi import Ossapi

api = Ossapi("API_KEY")
json = api.get_replay({"m": "0", "b": "1776628", "u": "3256299"})
# either strings or ints will work. Returns something like
# `{"content":"XQAAIA....3fISw=","encoding":"base64"}`
```

## api v2

We also provide support for [api v2](https://osu.ppy.sh/docs/index.html) (note: requires python 3.8+).

This support is in beta, so if you would like to use ossapi for api v2, you will need to run the following to download the latest beta release:

```bash
pip install --pre --upgrade ossapi
```

### Usage

You will need to create an oauth client on your settings page (<https://osu.ppy.sh/home/account/edit>), then use the client's id, secret, and redirect_uri to authenticate.

```python
from ossapi import *

# authenticates with client credentials grant (grants guest user access,
# some endpoints are unavailable to you, such as `download_score`)
api = OssapiV2(client_id, client_secret)
# if you also pass `redirect_uri`, we authenticate with authorization
# code grant, which grants full permissions. Note that `redirect_uri` must
# match the redirect uri specified in the oauth client you created, and
# must also be to a port on localhost (eg `"http://localhost:3918/"`).
# You will be redirected to an authorization page for the client in your
# browser the first time you instantiate `OssapiV2`. The token received
# is used instead for every subsequent instantiation instead of authorizing
# again.
api = OssapiV2(client_id, client_secret, redirect_uri)

# example usages of endpoints
print(api.ranking("osu", RankingType.PERFORMANCE, country="US").ranking[0].user.username)
print(api.user_scores(12092800, "best")[0].accuracy)
print(api.beatmap(beatmap_id=221777).last_updated)
print(api.beatmap_user_score(beatmap_id=221777, user_id=2757689).score.mods)
print(api.search(query="peppy").user.data[0].profile_colour)
print(api.comment(comment_id=1).comments[0].message)
print(api.download_score(mode="osu", score_id=2797309065))
print(api.search_beatmaps({"title": "the big black"}).beatmapsets[0].title)
print(api.search_beatmaps(cursor=api.search_beatmaps().cursor).beatmapsets[0].title)
print(api.beatmapsets_events(types=[BeatmapsetEventType.ISSUE_REOPEN]).events[0].type)
print(api.user(12092800).playstyle)

```

Work on api v2's endpoints is ongoing. Some endpoints are not currently implemented. You can track our progress towards implementing all documented api v2 endpoints here: https://github.com/circleguard/ossapi/issues/14.
