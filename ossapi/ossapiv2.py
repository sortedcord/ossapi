from typing import get_type_hints, get_origin, get_args, Union, TypeVar
import dataclasses
import logging
import webbrowser
import socket
import pickle
from pathlib import Path
from tempfile import NamedTemporaryFile

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from ossapi.models import (Beatmap, BeatmapUserScore, ForumTopicAndPosts,
    Search, BeatmapExtended, CommentBundle, ReplayScore, Cursor)
from ossapi.mod import Mod

def is_model_type(obj):
    # almost every model we have is a dataclass, but we do have a unique one,
    # ``Cursor``, which we also need to consider as a model type.
    return obj is Cursor or dataclasses.is_dataclass(obj)

class OssapiV2:
    TOKEN_URL = "https://osu.ppy.sh/oauth/token"
    BASE_URL = "https://osu.ppy.sh/api/v2"
    SCOPE = ["public"]

    def __init__(self, client_id, client_secret, redirect_uri=None,
        scope=["public"]):

        self.session = self.authenticate(client_id, client_secret, redirect_uri,
            scope)
        self.log = logging.getLogger(__name__)
        # api responses often differ from their documentation. I'm not going to
        # go and reverse engineer every endpoint (which could change at any
        # moment), so instead we have this stopgap: we consider every attribute
        # to be nullable, so if it's missing from the api response we just give
        # it a value of ``None``. Normally this only happens for ``Optional[X]``
        # type hints. TODO turn this off when the api is more stable or has
        # better documentation.
        self.consider_everything_nullable = True

    def authenticate(self, client_id, client_secret, redirect_uri, scope):
        # Prefer saved sessions to re-authenticating. Furthermore, prefer the
        # authorization code grant over the client credentials grant if both
        # exist.
        token_file = Path(__file__).parent / "authorization_code.pickle"
        if token_file.is_file():
            with open(token_file, "rb") as f:
                token = pickle.load(f)
            return OAuth2Session(client_id, token=token)

        token_file = Path(__file__).parent / "client_credentials.pickle"
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
        auto_refresh_kwargs = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        client = BackendApplicationClient(client_id=client_id, scope=["public"])

        oauth = OAuth2Session(client=client,
            auto_refresh_kwargs=auto_refresh_kwargs)

        token = oauth.fetch_token(token_url=self.TOKEN_URL, client_id=client_id,
            client_secret=client_secret)
        path = Path(__file__).parent / "client_credentials.pickle"
        with open(path, "wb+") as f:
            pickle.dump(token, f)

        return oauth

    def _authorization_code_grant(self, client_id, client_secret, redirect_uri,
        scope):
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        authorization_url, _state = oauth.authorization_url("https://osu.ppy.sh/oauth/authorize")

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
        token = oauth.fetch_token("https://osu.ppy.sh/oauth/token",
            client_id=client_id, client_secret=client_secret, code=code)
        path = Path(__file__).parent / "authorization_code.pickle"
        with open(path, "wb+") as f:
            pickle.dump(token, f)

        return oauth

    def _get(self, type_, url, params={}):
        r = self.session.get(f"{self.BASE_URL}{url}", params=params)
        json = r.json()
        obj = self._instantiate(type_, **json)
        obj = self._resolve_annotations(obj)
        return obj

    def _resolve_annotations(self, obj):
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

            # TODO is this the right place to do this conversion (for datetime
            # attributes too)? Should it happen lower down in our
            # ``if is_model_type(type_) or is_model_type(origin) or is_list:``
            # check?
            if type_ is Mod:
                self.log.debug("Found a mod attribute, converting to a Mod")
                value = Mod(value)
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

            if origin is list and (is_model_type(args[0]) or isinstance(args[0], TypeVar)):
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
        # TODO this doesn't work when type_ is a _GenericAlias, which isn't
        # surprising - what is surprising is that it lets us instantiate that
        # type with **kwargs and it works fine. Needs more investigation.
        try:
            type_hints = get_type_hints(type_)
        except TypeError:
            return type_(**kwargs)

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

    def beatmap_lookup(self, checksum=None, filename=None, id_=None):
        params = {"checksum": checksum, "filename": filename, "id": id_}
        return self._get(Beatmap, "/beatmaps/lookup", params)

    def beatmap_user_score(self, beatmap, user, mode=None, mods=None):
        params = {"mode": mode, "mods": mods}
        return self._get(BeatmapUserScore,
            f"/beatmaps/{beatmap}/scores/users/{user}", params)

    def beatmap(self, beatmap):
        return self._get(BeatmapExtended, f"/beatmaps/{beatmap}")

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
        params = {"commentable_type": commentable_type, "commentable_id":
            commentable_id, "cursor": cursor, "parent_id": parent_id,
            "sort": sort}
        return self._get(CommentBundle, "/comments", params)

    def comment(self, comment):
        """
        https://osu.ppy.sh/docs/index.html#get-a-comment
        """
        return self._get(CommentBundle, f"/comments/{comment}")

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

    def score(self, mode, score):
        return self._get(ReplayScore, f"/scores/{mode}/{score}")

    def score_download(self, mode, score):
        r = self.session.get(f"{self.BASE_URL}/scores/{mode}/{score}/download")

        tempfile = NamedTemporaryFile(mode="wb", delete=False)
        with tempfile as f:
            f.write(r.content)

        return tempfile.name
