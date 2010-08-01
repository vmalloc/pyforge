from ut_utils import ForgeTestCase
from forge import UnexpectedCall
from forge import ExpectedCallsNotFound
from forge import SignatureException

def _func1(a, b, c=2):
    raise NotImplementedError()

def _func2(a, b, c=2, *args, **kwargs):
    raise NotImplementedError()

class FunctionMockRecordReplayTest(ForgeTestCase):
    def setUp(self):
        super(FunctionMockRecordReplayTest, self).setUp()
        self.assertTrue(self.forge.is_recording())
        self.stub1 = self.forge.create_function_stub(_func1)
        self.stub2 = self.forge.create_function_stub(_func2)
    def tearDown(self):
        self.forge.verify()
        super(FunctionMockRecordReplayTest, self).tearDown()
    def test__record_replay_regular_functions(self):
        self.stub1(1, 2, 3)
        self.forge.replay()
        self.stub1(1, 2, 3)
        self.forge.verify()
    def test__record_replay_regular_functions_replay_different(self):
        self.stub1(1, 2, 3)
        self.forge.replay()
        self.stub1(a=1, b=2, c=3)
        self.forge.verify()
    def test__record_replay_not_recording_optional_argument(self):
        self.stub1(1, 2)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            self.stub1(1, 2, 2)
        self._assert_verify_expected_not_met(self.stub1)
        self.forge.reset()            
    def test__record_replay_no_actual_call(self):
        self.stub1(1, 2, 3)
        self.forge.replay()
        self._assert_verify_expected_not_met(self.stub1)
        self.forge.reset()
    def _assert_verify_expected_not_met(self, stub):
        with self.assertRaises(ExpectedCallsNotFound) as caught:
            self.forge.verify()
        expected_calls = caught.exception.calls
        self.assertEquals(len(expected_calls), 1)
        self.assertIs(expected_calls[0].target, stub)

class BadSignatureRecordReplay(ForgeTestCase):
    def test__record_bad_args(self):
        stub = self.forge.create_function_stub(_func1)
        with self.assertRaises(SignatureException):
            stub()
        with self.assertRaises(SignatureException):
            stub(1)
        with self.assertRaises(SignatureException):
            stub(1, 2, 3, d=4)
        # make sure nothing is recorded
        self.assertEquals(len(self.forge.queue), 0)

