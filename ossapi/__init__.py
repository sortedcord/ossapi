import sys
import logging

from ossapi.ossapi import (Ossapi, ReplayUnavailableException,
    InvalidKeyException, APIException)
from ossapi.ossapiv2 import OssapiV2, Grant, Scope
from ossapi.mod import Mod
from ossapi.replay import Replay
from ossapi.version import __version__

from oauthlib.oauth2 import AccessDeniedError, TokenExpiredError
from oauthlib.oauth2.rfc6749.errors import InsufficientScopeError

# TODO turn these back to explicit imports when ossapi (and api v2 itself) has
# stabilized a little bit
from ossapi.enums import *
from ossapi.models import *

# __all__ = ["Ossapi", "OssapiV2", "__version__", "Mod"]

# we need to explicitly set a handler for the logging module to be happy
handler = logging.StreamHandler()
logging.getLogger("ossapi").addHandler(handler)
