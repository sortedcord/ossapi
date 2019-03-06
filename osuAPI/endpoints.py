# can't use nested enums, so even though it hurts my soul...nested classes it is
class ENDPOINTS():
    class GET_BEATMAPS():
        EXTENSION = "get_beatmaps"
        REQUIRED = []  # this is according to https://github.com/ppy/osu-api/wiki
        POSSIBLE = ["since", "s", "b", "u", "type", "m", "a", "h", "limit"]

    class GET_MATCH():
        EXTENSION = "get_match"
        REQUIRED = ["mp"]
        POSSIBLE = ["mp"]

    class GET_SCORES():
        EXTENSION = "get_scores"
        REQUIRED = ["b"]
        POSSIBLE = ["b", "u", "m", "mods", "type", "limit"]

    class GET_REPLAY():
        EXTENSION = "get_replay"
        REQUIRED = ["m", "b", "u"]
        POSSIBLE = ["m", "b", "u", "mods"]

    class GET_USER():
        EXTENSION = "get_user"
        REQUIRED = ["u"]
        POSSIBLE = ["u", "m", "type", "event_days"]

    class GET_USER_BEST():
        EXTENSION = "get_user_best"
        REQUIRED = ["u"]
        POSSIBLE = ["m", "u", "limit", "type"]

    class GET_USER_RECENT():
        EXTENSION = "get_user_recent"
        REQUIRED = ["u"]
        POSSIBLE = ["m", "u", "limit", "type"]
