import requests
from json.decoder import JSONDecodeError
import logging

from ossapi.endpoints import ENDPOINTS

class Ossapi():
    """
    A simple api wrapper. Every public method takes a dict as its argument,
    mapping keys to values.

    No attempt is made to ratelimit the connection or catch request errors.
    This is left to the user implementation.
    """

    # how long, in seconds, to wait before raising a `requests.Timeout` exception
    TIMEOUT = 15

    def __init__(self, key):
        """Initializes an API instance."""
        self._key = key
        self.log = logging.getLogger(__name__)
        self.base_url = "https://osu.ppy.sh/api/{}?k=" + self._key

    def _check_parameters(self, ep, params):
        """Checks that all parameters required by the endpoint are present in the passed arguments,
        and that all passed arguments are possible parameters for the endpoint."""

        any_group_satisfied = False
        for group in ep.REQUIRED:
            if all(required_param in params for required_param in group):
                any_group_satisfied = True

        if not any_group_satisfied:
            raise ValueError(f"Got parameters {params}, expected one of {ep.REQUIRED}")

        for key in params:
            if key not in ep.POSSIBLE:
                raise ValueError(f"Got {key}, expected one of {ep.POSSIBLE}")

    def _extend_url(self, url, params):
        """Adds every key/value pair in the params dict to the url."""
        # filter out None parameters
        params = {k:v for k,v in params.items() if v is not None}
        for key in params:
            url = url + "&{}={}".format(key, params[key])
        return url

    def _process_url(self, url):
        """Makes a request to the osu api and returns the json response.
        Returns a dictionary of 'error' to 'The api broke.' if no valid
        json could be decoded (ie if a JSONDecodeError is thrown while
        decoding the response)"""
        response = requests.get(url, timeout=self.TIMEOUT)
        try:
            ret = response.json()
        except JSONDecodeError:
            self.log.exception("JSONDecodeError, response: %r, response.text: %r", response, response.text)
            ret = {"error": "The api broke."}
        return ret

    def get_beatmaps(self, params):
        """Retrieves a list of maps an their information."""
        ep = ENDPOINTS.GET_BEATMAPS
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)

    def get_match(self, params):
        """Retrieves information about a multiplayer match."""
        ep = ENDPOINTS.GET_MATCH
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)

    def get_scores(self, params):
        """Retrieves score data about the leaderboards of a map."""
        ep = ENDPOINTS.GET_SCORES
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)

    def get_replay(self, params):
        """Retrieves replay data by a user on a map."""
        ep = ENDPOINTS.GET_REPLAY
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)

    def get_user(self, params):
        """Retrieves information about a user."""
        ep = ENDPOINTS.GET_USER
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)

    def get_user_best(self, params):
        """Retrieves top scores of a user."""
        ep = ENDPOINTS.GET_USER_BEST
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)

    def get_user_recent(self, params):
        """Retrieves latest scores of a user."""
        ep = ENDPOINTS.GET_USER_RECENT
        self._check_parameters(ep, params)
        url = self.base_url.format(ep.EXTENSION)
        url = self._extend_url(url, params)
        return self._process_url(url)
