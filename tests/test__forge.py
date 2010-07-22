from ut_utils import TestCase
from forge import Forge

class ForgeTest(TestCase):
    def setUp(self):
        super(ForgeTest, self).setUp()
        self.forge = Forge()
    def test__replaying(self):
        self.assertFalse(self.forge.isReplaying())
        self.forge.replay()
        self.assertTrue(self.forge.isReplaying())
    def test__reset(self):
        self.test__replaying()
        self.forge.reset()
        self.assertFalse(self.forge.isReplaying())
