from unittest import TestCase

from tests import api

class TestMethodTypeConversion(TestCase):
    def test_beatmap_as_parameter(self):
        # make sure we can pass the full model in place of an id
        beatmap = api.beatmap(221777)
        self.assertEqual(api.beatmap_scores(beatmap),
            api.beatmap_scores(beatmap.id))

class TestExpandableModels(TestCase):
    def test_expand_user(self):
        user = api.search(query="tybug").user.data[0]
        # ``statistics`` is only available on User models, so make sure it's not
        # present before expanding and is present afterwards
        self.assertIsNone(user.statistics)
        user = user.expand()
        self.assertIsNotNone(user.statistics)
