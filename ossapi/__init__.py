import sys
import logging

from ossapi.ossapi import (Ossapi, ReplayUnavailableException,
    InvalidKeyException, APIException)

# OssapiV2 requires python 3.8+
if sys.version_info[1] >= 8:
    from ossapi.ossapiv2 import OssapiV2, Grant

from ossapi.mod import Mod
from ossapi.version import __version__

# TODO turn these back to explicit imports when ossapi (and api v2 itself) has
# stabilized a little bit
from ossapi.enums import *
from ossapi.models import *

# __all__ = ["Ossapi", "OssapiV2", "__version__", "Mod"]

# we need to explicitly set a handler for the logging module to be happy
handler = logging.StreamHandler()
logging.getLogger("ossapi").addHandler(handler)
