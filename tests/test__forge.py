from ut_utils import TestCase
from forge import Forge

class ForgeTest(TestCase):
    def setUp(self):
        super(ForgeTest, self).setUp()
        self.forge = Forge()
    def assertRecording(self):
        self.assertFalse(self.forge.is_replaying())
        self.assertTrue(self.forge.is_recording())
    def assertReplaying(self):
        self.assertTrue(self.forge.is_replaying())
        self.assertFalse(self.forge.is_recording())
        
    def test__replaying(self):
        self.assertRecording()
        self.forge.replay()
        self.assertReplaying()
        self.forge.verify()
        self.assertReplaying()
    def test__reset(self):
        self.test__replaying()
        self.forge.queue._queue = [1, 2, 3, 4]
        self.forge.reset()
        self.assertRecording()
        self.assertEquals(len(self.forge.queue), 0)
        
