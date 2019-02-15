# osuAPI

OsuAPI is a minimal python wrapper for the osu api. This wrapper was created for, and is used in, the [circleguard](https://github.com/circleguard/circleguard) project. Passed keys (endpoint parameter key/value pairs, not the api key) are checked to make sure the api will accept them, and that all required keys are present. No attempt is made to check http status codes or retry requests that fail.

### Usage

To install:
```bash
$ pip install git+https://github.com/circleguard/osu-api
```

To use:
```python
from osuAPI import OsuAPI

api = OsuAPI("API_KEY")
api.get_replay({"m": "0", "b": "1776628", "u": "3256299"})
# either strings or ints will work. Returns something like `{"content":"XQAAIA....3fISw=","encoding":"base64"}`
```
