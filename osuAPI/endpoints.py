# can't use nested enums, so even though it hurts my soul...nested classes it is
class ENDPOINTS():
    class GET_SCORES():
        EXTENSION = "get_scores"
        REQUIRED = ["b"]
        POSSIBLE = ["b", "u", "m", "mods", "type", "limit"]

    class GET_REPLAY():
        EXTENSION = "get_replay"
        REQUIRED = ["m", "b", "u"]
        POSSIBLE = ["m", "b", "u", "mods"]
