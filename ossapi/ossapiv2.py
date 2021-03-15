from typing import get_type_hints, get_origin, get_args, Union, TypeVar

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from ossapi.models import (model_types, Beatmap, BeatmapUserScore, ForumTopicAndPosts,
    Search, BeatmapExtended, CommentBundle)


class OssapiV2:
    TOKEN_URL = "https://osu.ppy.sh/oauth/token"
    BASE_URL = "https://osu.ppy.sh/api/v2"
    SCOPE = ["public"]

    def __init__(self, client_id, client_secret):
        auto_refresh_kwargs = {
            "client_id": client_id,
            "client_secret": client_secret
        }

        client = BackendApplicationClient(client_id=client_id, scope=self.SCOPE)

        oauth = OAuth2Session(client=client,
            auto_refresh_kwargs=auto_refresh_kwargs,
            token_updater=self._update_token)
        token = oauth.fetch_token(token_url=self.TOKEN_URL, client_id=client_id,
            client_secret=client_secret)
        self._update_token(token)
        self.session = oauth

    def _get(self, url, locals_, type_):
        # ``locals()`` includes the ``self`` argument which we need to remove.
        locals_ = {k:v for k,v in locals_.items() if k != "self"}
        # some of our params are named eg ``id_`` to avoid conflicting with
        # python builtins, but we need to pass eg ``id`` to the api.
        locals_ = {k[:-1]:v for k,v in locals_.items() if k.endswith("_")}

        r = self.session.get(f"{self.BASE_URL}{url}", params=locals_)
        json = r.json()
        obj = type_(**json)
        obj = self._resolve_annotations(obj)
        return obj

    def _resolve_annotations(self, obj):
        # we want to get the annotations of inherited members as well, which is
        # why we pass ``type(obj)`` instead of just ``obj``, which would only
        # return annotations for attributes defined in ``obj`` and not its
        # inherited attributes.
        annotations = get_type_hints(type(obj))
        for attr, value in obj.__dict__.items():
            # we use this attribute later if we encounter an attribute which
            # has been instantiated generically, but we don't need to do
            # anything with it now.
            if attr == "__orig_class__":
                continue

            # we need to handle lists specially, as we iterate over the data
            # and then instantiate ``type_`` with each entry in the data to
            # form a new list.
            is_list = False

            type_ = annotations[attr]
            origin = get_origin(type_)
            args = get_args(type_)

            # check if this type is ``Optional[X]``, which is equivalent to
            # ``Union[X, None]``. If it is an optional, we want to convert the
            # json data to an instance of X, but only if we've actually received
            # data for it.
            if origin is Union and args[1] is type(None):
                # leaving these assertions in to help me catch errors in my
                # reasoning until I better understand python's typing.
                assert len(args) == 2
                type_ = args[0]
                origin = get_origin(type_)
                args = get_args(type_)
            elif origin is list:
                assert len(args) == 1
                is_list = True
                # check if the list has been instantiated generically; if so,
                # use the concrete type backing the generic type.
                if isinstance(args[0], TypeVar):
                    # this attribute, ``__orig_class__``, is how we get the
                    # concrete type of a generic. See
                    # https://stackoverflow.com/a/60984681 and
                    # https://www.python.org/dev/peps/pep-0560/#mro-entries.
                    type_ = get_args(obj.__orig_class__)[0]
                # otherwise, it's been instantiated with a concrete type, so
                # use that type.
                else:
                    type_ = args[0]
                origin = get_origin(type_)
                args = get_args(type_)

            # either we ourself are a model type (eg ``Search``), or we are
            # a special indexed type (eg ``type_ == SearchResult[UserCompact]``,
            # ``origin == UserCompact``). In either case we want to instantiate
            # ``type_``.
            if type_ in model_types or origin in model_types:
                # special handling for lists; otherwise, just instantiate with
                # the actual value of ``value``.
                if is_list:
                    new_value = []
                    for entry in value:
                        entry = type_(**entry)
                        new_value.append(entry)
                    value = new_value
                else:
                    value = type_(**value)
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

        return obj

    def _update_token(self, token):
        self.token = token

    # we pass the arguments to these functions via ``locals()`` which pylint
    # doesn't pick up on, so it thinks they're unused.
    # pylint: disable=unused-argument
    def beatmap_lookup(self, checksum=None, filename=None, id_=None):
        return self._get("/beatmaps/lookup", locals(), Beatmap)

    def beatmap_user_score(self, beatmap, user, mode=None, mods=None):
        return self._get(f"/beatmaps/{beatmap}/scores/users/{user}",
            locals(), BeatmapUserScore)

    def beatmap(self, beatmap):
        return self._get(f"/beatmaps/{beatmap}", locals(), BeatmapExtended)

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
        return self._get("/comments", locals(), CommentBundle)

    def comment(self, comment):
        """

        https://osu.ppy.sh/docs/index.html#get-a-comment
        """
        return self._get(f"/comments/{comment}", locals(), CommentBundle)

    def topic(self, topic, cursor=None, sort=None, limit=None, start=None,
        end=None):
        """
        A topic and its posts.

        https://osu.ppy.sh/docs/index.html#get-topic-and-posts
        """
        return self._get(f"/forums/topics/{topic}", locals(),
            ForumTopicAndPosts)

    def search(self, mode="all", query=None, page=None):
        return self._get("/search", locals(), Search)
