[![PyPI version](https://badge.fury.io/py/ossapi.svg)](https://pypi.org/project/ossapi/)

# ossapi

ossapi (so called to avoid pypi naming conflicts with the existing osuapi) is a minimal python wrapper for the osu! api. This wrapper was created for, and is used in, [circleguard](https://github.com/circleguard/circleguard). Passed params are checked to make sure the api will accept them, and that all required params are present. No attempt is made to check http status codes or retry requests that fail.

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

## osu api v2

We also provide support for [api v2](https://osu.ppy.sh/docs/index.html). **(Note: requires python 3.8+)**

You can create an oauth client on your settings page (<https://osu.ppy.sh/home/account/edit>), then use the client's id, secret, and redirect_uri to authenticate.

```python
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
print(api.beatmap(beatmap_id=221777).status)
print(api.beatmap_user_score(beatmap_id=221777, user_id=2757689).score.mods)
print(api.search(query="peppy").user.data[0].profile_colour)
print(api.comment(comment_id=1).cursor.created_at)
print(api.download_score(mode="osu", score_id=2797309065))
print(api.search_beatmaps("the big black").beatmapsets[0].title)
```

Work on api v2's endpoints is ongoing and unstable. Consider support for it to be in beta.
