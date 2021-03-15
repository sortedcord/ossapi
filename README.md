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
from ossapi import ossapi

api = ossapi("API_KEY")
json = api.get_replay({"m": "0", "b": "1776628", "u": "3256299"})
# either strings or ints will work. Returns something like `{"content":"XQAAIA....3fISw=","encoding":"base64"}`
```
