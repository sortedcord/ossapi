from typing import (get_type_hints, get_origin, get_args, Union, TypeVar,
    Optional, List)
import dataclasses
import logging
import webbrowser
import socket
import pickle
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime
from enum import Enum
from urllib.parse import unquote

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from ossapi.models import (Beatmap, BeatmapUserScore, ForumTopicAndPosts,
    Search, CommentBundle, Cursor, Score, BeatmapSearchResult,
    ModdingHistoryEventsBundle, User, Rankings)
from ossapi.mod import Mod
from ossapi.enums import GameMode, ScoreType, RankingFilter, RankingType

GameModeT = Union[GameMode, str]
ScoreTypeT = Union[ScoreType, str]
ModT = Union[Mod, str, int, list]
RankingFilterT = Union[RankingFilter, str]
RankingTypeT = Union[RankingType, str]

class OssapiV2:
    TOKEN_URL = "https://osu.ppy.sh/oauth/token"
    AUTH_CODE_URL = "https://osu.ppy.sh/oauth/authorize"
    BASE_URL = "https://osu.ppy.sh/api/v2"

    def __init__(self, client_id, client_secret, redirect_uri=None,
        scopes=["public"]):
        self.log = logging.getLogger(__name__)

        self.session = self.authenticate(client_id, client_secret, redirect_uri,
            scopes)

    def authenticate(self, client_id, client_secret, redirect_uri, scopes):
        # Prefer saved sessions to re-authenticating. Furthermore, prefer the
        # authorization code grant over the client credentials grant if both
        # exist.
        token_file = Path(__file__).parent / "authorization_code.pickle"
        if token_file.is_file():
            with open(token_file, "rb") as f:
                token = pickle.load(f)
            return self._auth_oauth_session(client_id, client_secret, scopes,
                token=token)

        token_file = Path(__file__).parent / "client_credentials.pickle"
        # TODO I think this breaks if the token is expired?
        if token_file.is_file():
            with open(token_file, "rb") as f:
                token = pickle.load(f)
            return OAuth2Session(client_id, token=token)

        # if redirect_uri is not passed, assume the user wanted to use the
        # client credentials grant.
        if not redirect_uri:
            if scopes != ["public"]:
                raise ValueError(f"`scopes` must be ['public'] if the "
                    f"client credentials grant is used. Got {scopes}")
            return self._client_credentials_grant(client_id, client_secret)
        return self._authorization_code_grant(client_id, client_secret,
            redirect_uri, scopes)

    def _client_credentials_grant(self, client_id, client_secret):
        client = BackendApplicationClient(client_id=client_id, scope=["public"])
        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(token_url=self.TOKEN_URL,
            client_id=client_id, client_secret=client_secret)
        self._save_token(token, "client")

        return oauth

    def _authorization_code_grant(self, client_id, client_secret, redirect_uri,
        scopes):
        oauth = self._auth_oauth_session(client_id, client_secret, scopes,
            redirect_uri=redirect_uri)
        authorization_url, _state = oauth.authorization_url(self.AUTH_CODE_URL)
        webbrowser.open(authorization_url)

        # open up a temporary socket so we can receive the GET request to the
        # callback url
        port = int(redirect_uri.rsplit(":", 1)[1].split("/")[0])
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(("localhost", port))
        serversocket.listen(1)
        connection, _ = serversocket.accept()
        # arbitrary "large enough" byte receive size
        data = str(connection.recv(8192))
        connection.send(b"HTTP/1.0 200 OK\n")
        connection.send(b"Content-Type: text/html\n")
        connection.send(b"\n")
        connection.send(b"""<html><body>
            <h2>Ossapi has received your authentication.</h2> You
            can now close this tab safely.
            </body></html>
        """)
        connection.close()
        serversocket.close()

        code = data.split("code=")[1].split("&state=")[0]
        token = oauth.fetch_token(self.TOKEN_URL, client_id=client_id,
            client_secret=client_secret, code=code)
        self._save_token(token, "auth")

        return oauth

    def _auth_oauth_session(self, client_id, client_secret, scopes, *,
        token=None, redirect_uri=None):
        auto_refresh_kwargs = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        return OAuth2Session(client_id, token=token, redirect_uri=redirect_uri,
            auto_refresh_url=self.TOKEN_URL,
            auto_refresh_kwargs=auto_refresh_kwargs,
            token_updater=lambda token: self._save_token(token, "auth"),
            scope=scopes)

    def _save_token(self, token, flow):
        self.log.info(f"saving token to pickle file for flow {flow}")
        filename = ("authorization_code.pickle" if flow == "auth" else
            "client_credentials.pickle")
        path = Path(__file__).parent / filename
        with open(path, "wb+") as f:
            pickle.dump(token, f)

    def _get(self, type_, url, params={}):
        params = self._format_params(params)
        r = self.session.get(f"{self.BASE_URL}{url}", params=params)
        self.log.info(f"made request to {r.request.url}")
        json = r.json()
        # TODO this should just be ``if "error" in json``, but for some reason
        # ``self.search_beatmaps`` always returns an error in the response...
        # open an issue on osu-web?
        if len(json) == 1 and "error" in json:
            raise ValueError(f"api returned an error of `{json['error']}` for "
                f"a request to {unquote(r.request.url)}")
        return self._instantiate_type(type_, json)

    def _format_params(self, params):
        for key, value in params.copy().items():
            if isinstance(value, list):
                # we need to pass multiple values for this key, so make its
                # value a list https://stackoverflow.com/a/62042144
                params[f"{key}[]"] = []
                for v in value:
                    params[f"{key}[]"].append(self._format_value(v))
                del params[key]
            elif isinstance(value, Cursor):
                new_params = self._format_params(value.__dict__)
                for k, v in new_params.items():
                    params[f"cursor[{k}]"] = v
                del params[key]
            elif isinstance(value, Mod):
                params[f"{key}[]"] = value.decompose()
                del params[key]
            else:
                params[key] = self._format_value(value)
        return params

    def _format_value(self, value):
        if isinstance(value, datetime):
            return 1000 * int(value.timestamp())
        if isinstance(value, Enum):
            return value.value
        return value

    def _resolve_annotations(self, obj):
        """
        This is where the magic happens. Since python lacks a good
        deserialization library, I've opted to use type annotations and type
        annotations only to convert json to objects. A breakdown follows.

        Every endpoint defines a base object, let's say it's a ``Score``. We
        first instantiate this object with the json we received. This is easy to
        do because (almost) all of our objects are dataclasses, which means we
        can pass the json as ``Score(**json)`` and since the names of our fields
        coincide with the names of the api json keys, everything works.

        This populates all of the surface level members, but nested attributes
        which are annotated as another dataclass object will still be dicts. So
        we traverse down the tree of our base object's attributes (depth-first,
        though I'm pretty sure BFS would work just as well), looking for any
        attribute with a type annotation that we need to deal with. For
        instance, ``Score`` has a ``beatmap`` attribute, which is annotated as
        ``Optional[Beatmap]``. We ignore the optional annotation (since we're
        looking at this attribute, we must have received data for it, so it's
        nonnull) and then instantiate the ``beatmap`` attribute the same way
        we instantiated the ``Score`` - with ``Beatmap(**json)``. Of course, the
        variables will look different in the method (``type_(**value)``).

        Finally, when traversing the attribute tree, we also look for attributes
        which aren't dataclasses, but we still need to convert. For instance,
        any attribute with an annotation of ``datetime`` or ``Mod`` we convert
        to a ``datetime`` and ``Mod`` object respectively.

        This code is arguably trying to be too smart for its own good, but I
        think it's very elegant from the perspective of "just add a dataclass
        that mirrors the api's objects and everything works". Will hopefully
        make changing our dataclasses to account for breaking api changes in
        the future trivial as well.

        And if I'm being honest, it was an excuse to learn the internals of
        python's typing system.
        """
        # we want to get the annotations of inherited members as well, which is
        # why we pass ``type(obj)`` instead of just ``obj``, which would only
        # return annotations for attributes defined in ``obj`` and not its
        # inherited attributes.
        annotations = get_type_hints(type(obj))
        self.log.debug(f"resolving annotations for type {type(obj)}")
        for attr, value in obj.__dict__.items():
            # we use this attribute later if we encounter an attribute which
            # has been instantiated generically, but we don't need to do
            # anything with it now.
            if attr == "__orig_class__":
                continue
            # when we instantiate types, we explicitly fill in optional
            # attributes with ``None``. This means they're in ``obj.__dict__``
            # and so we see them here. We don't want to do anything with them,
            # so skip.
            if value is None:
                continue
            self.log.debug(f"resolving attribute {attr}")

            type_ = annotations[attr]
            value = self._instantiate_type(type_, value, obj)
            if not value:
                continue
            setattr(obj, attr, value)
        self.log.debug(f"resolved annotations for type {type(obj)}")
        return obj

    def _instantiate_type(self, type_, value, obj=None):
        origin = get_origin(type_)
        args = get_args(type_)

        # if this type is an optional, "unwrap" it to get the true type.
        # We don't care about the optional annotation in this context
        # because if we got here that means we were passed a value for this
        # attribute, so we know it's defined and not optional.
        if self._is_optional(type_):
            # leaving these assertions in to help me catch errors in my
            # reasoning until I better understand python's typing.
            assert len(args) == 2
            type_ = args[0]
            origin = get_origin(type_)
            args = get_args(type_)

        # validate that the values we're receiving are the types we expect them
        # to be
        if self._is_primitive_type(type_):
            if not self._is_compatible_type(value, type_):
                raise TypeError(f"expected type {type_} for value {value}, got "
                    f"type {type(value)}")

        if self._is_base_type(type_):
            self.log.debug(f"instantiating base type {type_}")
            return type_(value)

        if origin is list and (self._is_model_type(args[0]) or
            isinstance(args[0], TypeVar)):
            assert len(args) == 1
            # check if the list has been instantiated generically; if so,
            # use the concrete type backing the generic type.
            if isinstance(args[0], TypeVar):
                # ``__orig_class__`` is how we can get the concrete type of
                # a generic. See https://stackoverflow.com/a/60984681 and
                # https://www.python.org/dev/peps/pep-0560/#mro-entries.
                type_ = get_args(obj.__orig_class__)[0]
            # otherwise, it's been instantiated with a concrete model type,
            # so use that type.
            else:
                type_ = args[0]
            new_value = []
            for entry in value:
                entry = self._instantiate(type_, **entry)
                # if the list entry is a model type, we need to resolve it
                # instead of just sticking it into the list, since its children
                # might still be dicts and not model instances.
                if self._is_model_type(type_):
                    entry = self._resolve_annotations(entry)
                new_value.append(entry)
            return new_value

        # either we ourself are a model type (eg ``Search``), or we are
        # a special indexed type (eg ``type_ == SearchResult[UserCompact]``,
        # ``origin == UserCompact``). In either case we want to instantiate
        # ``type_``.
        if not self._is_model_type(type_) and not self._is_model_type(origin):
            return None
        value = self._instantiate(type_, **value)
        # we need to resolve the annotations of any nested model types before we
        # set the attribute. This recursion is well-defined because the base
        # case is when ``value`` has no model types, which will always happen
        # eventually.
        return self._resolve_annotations(value)

    def _instantiate(self, type_, **kwargs):
        self.log.debug(f"instantiating type {type_}")
        # TODO this doesn't work when type_ is a _GenericAlias, which isn't
        # surprising - what is surprising is that it lets us instantiate that
        # type with **kwargs and it works fine. Needs more investigation.
        try:
            type_hints = get_type_hints(type_)
        except TypeError:
            return type_(**kwargs)

        # replace any key names that are invalid python syntax with a valid
        # one. Note: this is relying on our models replacing an at sign with
        # an underscore when declaring attributes.
        # ``list(kwargs)`` to make a copy of it so we can modify kwargs while
        # iterating.
        for key in list(kwargs):
            kwargs[key.replace("@", "_")] = kwargs.pop(key)

        # if we've annotated a class with ``Optional[X]``, and the api response
        # didn't return a value for that attribute, pass ``None`` for that
        # attribute.
        # This is so that we don't have to define a default value of ``None``
        # for each optional attribute of our models, since the default will
        # always be ``None``.
        for attribute, annotation in type_hints.items():
            if self._is_optional(annotation):
                if attribute not in kwargs:
                    kwargs[attribute] = None
        return type_(**kwargs)

    def _is_optional(self, type_):
        """
        ``Optional[X]`` is equivalent to ``Union[X, None]``.
        """
        return get_origin(type_) is Union and get_args(type_)[1] is type(None)

    def _is_model_type(self, type_):
        # almost every model we have is a dataclass, but we do have a unique
        # one, ``Cursor``, which we also need to consider as a model type.
        return type_ is Cursor or dataclasses.is_dataclass(type_)

    def _is_base_type(self, type_):
        """
        A "base" type is a type that is still instantiable (so not a primitive)
        but one that we don't need to recurse down its members to look for more
        model types (or more base types). The base type is responsible for
        cleaning up and/or modifying the data we give it, and we move on after
        instantiating it.

        Examples are enums, mods, and datetimes.
        """
        if not isinstance(type_, type):
            return False

        return issubclass(type_, (Enum, datetime, Mod))

    def _is_primitive_type(self, type_):
        if not isinstance(type_, type):
            return False

        return type_ in [int, float, str, bool]

    def _is_compatible_type(self, value, type_):
        # make an exception for an integer being instantiated as a float. In
        # the json we receive, eg ``pp`` can have a value of ``15833``, which is
        # interpreted as an int by our json parser even though ``pp`` is a
        # float.
        if type_ is float and isinstance(value, int):
            return True
        return isinstance(value, type_)


    # =========
    # Endpoints
    # =========


    # /beatmaps
    # ---------

    def beatmap_lookup(self,
        checksum: Optional[str] = None,
        filename: Optional[str] = None,
        beatmap_id: Optional[int] = None
    ) -> Beatmap:
        """
        https://osu.ppy.sh/docs/index.html#lookup-beatmap
        """
        params = {"checksum": checksum, "filename": filename, "id": beatmap_id}
        return self._get(Beatmap, "/beatmaps/lookup", params)

    def beatmap_user_score(self,
        beatmap_id: int,
        user_id: int,
        mode: Optional[GameModeT] = None,
        mods: Optional[ModT] = None
    ) -> BeatmapUserScore:
        """
        https://osu.ppy.sh/docs/index.html#get-a-user-beatmap-score
        """
        mode = GameMode(mode) if mode else None
        mods = Mod(mods) if mods else None
        params = {"mode": mode, "mods": mods}
        return self._get(BeatmapUserScore,
            f"/beatmaps/{beatmap_id}/scores/users/{user_id}", params)

    def beatmap(self, beatmap_id: int) -> Beatmap:
        """
        https://osu.ppy.sh/docs/index.html#get-beatmap
        """
        return self._get(Beatmap, f"/beatmaps/{beatmap_id}")


    # /comments
    # ---------

    def comments(self,
        commentable_type=None,
        commentable_id=None,
        cursor=None,
        parent_id=None,
        sort=None
    ) -> CommentBundle:
        """
        A list of comments and their replies, up to 2 levels deep.

        https://osu.ppy.sh/docs/index.html#get-comments

        Notes
        -----
        ``pinned_comments`` is only included when ``commentable_type`` and
        ``commentable_id`` are specified.
        """
        params = {"commentable_type": commentable_type,
            "commentable_id": commentable_id, "cursor": cursor,
            "parent_id": parent_id, "sort": sort}
        return self._get(CommentBundle, "/comments", params)

    def comment(self, comment_id: int) -> CommentBundle:
        """
        https://osu.ppy.sh/docs/index.html#get-a-comment
        """
        return self._get(CommentBundle, f"/comments/{comment_id}")


    # /forums
    # -------

    def topic(self,
        topic,
        cursor: Optional[Cursor] = None,
        sort=None,
        limit=None,
        start=None,
        end=None
    ) -> ForumTopicAndPosts:
        """
        A topic and its posts.

        https://osu.ppy.sh/docs/index.html#get-topic-and-posts
        """
        params = {"cursor": cursor, "sort": sort, "limit": limit,
            "start": start, "end": end}
        return self._get(ForumTopicAndPosts, f"/forums/topics/{topic}", params)


    # / ("home")
    # ----------

    def search(self,
        mode="all",
        query=None,
        page=None
    ) -> Search:
        """
        https://osu.ppy.sh/docs/index.html#search
        """
        params = {"mode": mode, "query": query, "page": page}
        return self._get(Search, "/search", params)


    # /rankings
    # ---------

    def ranking(self,
        mode: GameModeT,
        type_: RankingTypeT,
        country: Optional[str] = None,
        cursor: Optional[Cursor] = None,
        filter_: RankingFilterT = RankingFilter.ALL,
        spotlight: Optional[int] = None,
        variant: Optional[str] = None
    ) -> Rankings:
        """
        https://osu.ppy.sh/docs/index.html#get-ranking
        """
        mode = GameMode(mode).value
        type_ = RankingType(type_).value
        filter_ = RankingFilter(filter_)
        params = {"country": country, "cursor": cursor, "filter": filter_,
            "spotlight": spotlight, "variant": variant}
        return self._get(Rankings, f"/rankings/{mode}/{type_}", params=params)


    # /users
    # ------

    def user_scores(self,
        user_id: int,
        type_: ScoreTypeT,
        include_fails: Optional[bool] = None,
        mode: Optional[GameModeT] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Score]:
        """
        https://osu.ppy.sh/docs/index.html#get-user-scores
        """
        type_ = ScoreType(type_).value
        mode = GameMode(mode) if mode else None
        params = {"include_fails": include_fails, "mode": mode, "limit": limit,
            "offset": offset}
        return self._get(List[Score], f"/users/{user_id}/scores/{type_}",
            params)

    def user(self,
        user_id: int,
        mode: Optional[GameModeT] = None
    ) -> User:
        """
        https://osu.ppy.sh/docs/index.html#get-user
        """
        mode = GameMode(mode).value if mode else ""
        return self._get(User, f"/users/{user_id}/{mode}")


    # undocumented
    # ------------

    def score(self, mode: GameModeT, score_id: int) -> Score:
        mode = GameMode(mode)
        return self._get(Score, f"/scores/{mode.value}/{score_id}")

    def download_score(self, mode: GameModeT, score_id: int) -> str:
        mode = GameMode(mode).value
        r = self.session.get(f"{self.BASE_URL}/scores/{mode}/"
            f"{score_id}/download")

        tempfile = NamedTemporaryFile(mode="wb", delete=False)
        with tempfile as f:
            f.write(r.content)

        return tempfile.name

    def search_beatmaps(self,
        filters={},
        cursor: Optional[Cursor] = None
    ) -> BeatmapSearchResult:
        params = {"cursor": cursor}
        # filters should be passed as dict?
        params.update(filters)
        return self._get(BeatmapSearchResult, "/beatmapsets/search/", params)

    def beatmapsets_events(self,
        limit=None,
        page=None,
        user=None,
        types=None,
        min_date=None,
        max_date=None
    ) -> ModdingHistoryEventsBundle:
        """
        Beatmap history

        https://osu.ppy.sh/beatmapsets/events
        """
        # limit is 5-50
        # types listed here
        # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapsetEvent.php#L185
        params = {"limit": limit, "page": page, "user": user,
            "min_date": min_date, "max_date": max_date, "types": types}
        return self._get(ModdingHistoryEventsBundle, "/beatmapsets/events",
            params)
