import logging

from ossapi.ossapi import Ossapi
from ossapi.ossapiv2 import OssapiV2
from ossapi.mod import Mod
from ossapi.version import __version__

__all__ = ["Ossapi", "OssapiV2", "__version__", "Mod"]

# we need to explicitly set a handler for the logging module to be happy
handler = logging.StreamHandler()
logging.getLogger("ossapi").addHandler(handler)
