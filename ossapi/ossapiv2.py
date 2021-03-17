from typing import get_type_hints, get_origin, get_args, Union, TypeVar
import dataclasses
import logging
import webbrowser
import socket
import pickle
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime
from enum import Enum
from functools import partial

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from ossapi.models import (Beatmap, BeatmapUserScore, ForumTopicAndPosts,
    Search, CommentBundle, Cursor, Score, BeatmapSearchResult, ModdingHistoryEventsBundle)
from ossapi.mod import Mod

def is_model_type(obj):
    # almost every model we have is a dataclass, but we do have a unique one,
    # ``Cursor``, which we also need to consider as a model type.
    return obj is Cursor or dataclasses.is_dataclass(obj)

class OssapiV2:
    TOKEN_URL = "https://osu.ppy.sh/oauth/token"
    AUTH_CODE_URL = "https://osu.ppy.sh/oauth/authorize"
    BASE_URL = "https://osu.ppy.sh/api/v2"

    def __init__(self, client_id, client_secret, redirect_uri=None,
        scope=["public"]):
        self.log = logging.getLogger(__name__)

        self.session = self.authenticate(client_id, client_secret, redirect_uri,
            scope)
        # api responses sometimes differ from their documentation. I'm not going
        # to go and reverse engineer every endpoint (which could change at any
        # moment), so instead we have this stopgap: we consider every attribute
        # to be nullable, so if it's missing from the api response we just give
        # it a value of ``None``. Normally this only happens for ``Optional[X]``
        # type hints.
        self.consider_everything_nullable = False

    def authenticate(self, client_id, client_secret, redirect_uri, scope):
        # Prefer saved sessions to re-authenticating. Furthermore, prefer the
        # authorization code grant over the client credentials grant if both
        # exist.
        token_file = Path(__file__).parent / "authorization_code.pickle"
        if token_file.is_file():
            with open(token_file, "rb") as f:
                token = pickle.load(f)
            return self._auth_oauth_session(client_id, client_secret, scope,
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
            if scope != ["public"]:
                raise ValueError(f"scope must be ['public'] if the "
                    f"client credentials grant is used. Got {scope}")
            return self._client_credentials_grant(client_id, client_secret)
        return self._authorization_code_grant(client_id, client_secret,
            redirect_uri, scope)

    def _client_credentials_grant(self, client_id, client_secret):
        client = BackendApplicationClient(client_id=client_id, scope=["public"])
        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(token_url=self.TOKEN_URL,
            client_id=client_id, client_secret=client_secret)
        self._save_token(token, "client")

        return oauth

    def _authorization_code_grant(self, client_id, client_secret, redirect_uri,
        scope):
        oauth = self._auth_oauth_session(client_id, client_secret, scope,
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

    def _auth_oauth_session(self, client_id, client_secret, scope, *,
        token=None, redirect_uri=None):
        auto_refresh_kwargs = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        return OAuth2Session(client_id, token=token, redirect_uri=redirect_uri,
            auto_refresh_url=self.TOKEN_URL,
            auto_refresh_kwargs=auto_refresh_kwargs,
            token_updater=lambda: partial(self._save_token, flow="auth"),
            scope=scope)

    def _save_token(self, token, flow):
        self.log.info(f"saving token to pickle file for flow {flow}")
        filename = ("authorization_code.pickle" if flow == "auth" else
            "client_credentials.pickle")
        path = Path(__file__).parent / filename
        with open(path, "wb+") as f:
            pickle.dump(token, f)

    def _get(self, type_, url, params={}):
        r = self.session.get(f"{self.BASE_URL}{url}", params=params)
        json = r.json()
        obj = self._instantiate(type_, **json)
        obj = self._resolve_annotations(obj)
        return obj

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
            # when we do ``self._instantiate(type_, **json)`` above, we are
            # explicitly filling in optional attributes with ``None``. This
            # means they're in ``obj.__dict__`` and so we see them here. We
            # don't want to do anything with them, so skip.
            if value is None:
                continue
            self.log.debug(f"resolving attribute {attr}")

            # we need to handle lists specially, as we iterate over the data
            # and then instantiate ``type_`` with each entry in the data to
            # form a new list.
            is_list = False

            type_ = annotations[attr]
            origin = get_origin(type_)
            args = get_args(type_)

            # TODO is this the right place to do this conversion for these
            # types? Should it happen lower down in our
            # ``if is_model_type(type_) or is_model_type(origin) or is_list:``
            # check? Where does our list conversion fit into all this, is that
            # happening in the right place as well?
            if type_ is Mod:
                self.log.debug("Found a mod attribute, converting to a Mod")
                value = Mod(value)
                setattr(obj, attr, value)
                continue
            # ``issubclass`` only accepts classes so check if it's a class first
            # https://stackoverflow.com/a/395741
            if isinstance(type_, type) and issubclass(type_, Enum):
                # TODO could consolidate this and the above into a single method
                value = type_(value)
                setattr(obj, attr, value)
                continue
            if type_ is datetime:
                # the api returns two three of timestamps: two ISO 8601 formats
                # (eg "2018-09-11T08:45:49.000000Z" and
                # "2014-05-18T17:22:23+00:00") and a unix timestamp (eg
                # 1615385278000). We handle each case below.
                # Fully compliant ISO 8601 parsing is apparently a pain, and
                # the proper way to do this would be to use a third party
                # library, but I don't want to add any dependencies. This
                # stopgap seems to work for now, but may break in the future if
                # the api changes the timestamps they return.
                # see https://stackoverflow.com/q/969285.
                if value.endswith("Z"):
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
                else:
                    try:
                        # see if it's an int first, if so it's a unix timestamp.
                        # the api returns the timestamp in milliseconds but
                        # ``datetime.utcfromtimestamp`` expects it in seconds,
                        # so divide by 1000 to convert.
                        value = int(value) / 1000
                        value = datetime.utcfromtimestamp(value)
                    except ValueError:
                        # if it's not an int, assume it's the second form of ISO
                        # 8601
                        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
                setattr(obj, attr, value)
                continue

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

            if (origin is list and (is_model_type(args[0]) or
                isinstance(args[0], TypeVar))):
                assert len(args) == 1
                is_list = True
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
                origin = get_origin(type_)
                args = get_args(type_)

            # either we ourself are a model type (eg ``Search``), or we are
            # a special indexed type (eg ``type_ == SearchResult[UserCompact]``,
            # ``origin == UserCompact``). In either case we want to instantiate
            # ``type_``.
            if is_model_type(type_) or is_model_type(origin) or is_list:
                # special handling for lists; otherwise, just instantiate with
                # the actual value of ``value``.
                if is_list:
                    new_value = []
                    for entry in value:
                        entry = self._instantiate(type_, **entry)
                        # if the list entry is a model type, we need to resolve
                        # it instead of just sticking it into the list, since
                        # its children might still be dicts and not model
                        # instances
                        if is_model_type(type_):
                            entry = self._resolve_annotations(entry)
                        new_value.append(entry)
                    value = new_value
                else:
                    value = self._instantiate(type_, **value)
                    # we need to resolve the annotations of any nested model
                    # types before we set the attribute. This recursion is
                    # well-defined because the base case is when ``value`` has
                    # no model types, which will always happen eventually.
                    # We only want to resolve annotations if our value isn't a
                    # list. (TODO: why is this true? why can we always resolve
                    # annotations if we're not a list? are we not also passing
                    # primitives to ``resolve_annotations`` here?)
                    value = self._resolve_annotations(value)
                setattr(obj, attr, value)
        self.log.debug(f"resolved annotations for type {type(obj)}")
        return obj

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
            # see the comment in ``def __init__`` for more on
            # ``consider_everything_nullable``.
            # Cursor is special because it defines annotations in
            # ``__annotations__`` for which we don't want to give a value, so
            # ignore it even if we consider everything nullable.
            if ((self.consider_everything_nullable and type_ is not Cursor) or
                self._is_optional(annotation)):
                if attribute not in kwargs:
                    kwargs[attribute] = None
        return type_(**kwargs)

    def _is_optional(self, type_):
        """
        ``Optional[X]`` is equivalent to ``Union[X, None]``.
        """
        return get_origin(type_) is Union and get_args(type_)[1] is type(None)

    def beatmap_lookup(self, checksum=None, filename=None, beatmap_id=None):
        params = {"checksum": checksum, "filename": filename, "id": beatmap_id}
        return self._get(Beatmap, "/beatmaps/lookup", params)

    def beatmap_user_score(self, beatmap_id, user_id, mode=None, mods=None):
        params = {"mode": mode, "mods": mods}
        return self._get(BeatmapUserScore,
            f"/beatmaps/{beatmap_id}/scores/users/{user_id}", params)

    def beatmap(self, beatmap_id):
        return self._get(Beatmap, f"/beatmaps/{beatmap_id}")

    def comments(self, commentable_type=None, commentable_id=None, cursor=None,
        parent_id=None, sort=None):
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

    def comment(self, comment_id):
        """
        https://osu.ppy.sh/docs/index.html#get-a-comment
        """
        return self._get(CommentBundle, f"/comments/{comment_id}")

    def topic(self, topic, cursor=None, sort=None, limit=None, start=None,
        end=None):
        """
        A topic and its posts.

        https://osu.ppy.sh/docs/index.html#get-topic-and-posts
        """
        params = {"cursor": cursor, "sort": sort, "limit": limit,
            "start": start, "end": end}
        return self._get(ForumTopicAndPosts, f"/forums/topics/{topic}", params)

    def search(self, mode="all", query=None, page=None):
        params = {"mode": mode, "query": query, "page": page}
        return self._get(Search, "/search", params)

    def score(self, mode, score_id):
        return self._get(Score, f"/scores/{mode}/{score_id}")

    def download_score(self, mode, score_id):
        r = self.session.get(f"{self.BASE_URL}/scores/{mode}/{score_id}/download")

        tempfile = NamedTemporaryFile(mode="wb", delete=False)
        with tempfile as f:
            f.write(r.content)

        return tempfile.name

    def search_beatmaps(self, filters):
        return self._get(BeatmapSearchResult, f"/beatmapsets/search/{filters}")

    def beatmapsets_events(self, limit=None, page=None, user=None, types=None, min_date=None, max_date=None):
        """
        Beatmap history

        https://osu.ppy.sh/beatmapsets/events
        """
        # limit is 5-50
        # types listed here - https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapsetEvent.php#L185
        params = {"limit": limit, "page": page, "user": user, "types": types, "min_date": min_date, "max_date": max_date}
        return self._get(ModdingHistoryEventsBundle, "/beatmapsets/events", params)
