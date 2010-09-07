from ut_utils import TestCase
from ut_utils import Checkpoint
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
    def test__verified_replay_context(self):
        self.assertRecording()
        check_verify = Checkpoint()
        check_reset = Checkpoint()
        self.forge.verify = check_verify.trigger
        def _fake_reset():
            self.assertTrue(check_verify.called)
            check_reset.trigger()
        self.forge.reset = _fake_reset
        with self.forge.verified_replay_context():
            self.assertReplaying()
            self.assertFalse(check_verify.called)
            self.assertFalse(check_reset.called)
        self.assertTrue(check_reset.called)
        self.assertTrue(check_verify.called)
        # we don't assertRecording, since we stubbed out reset

