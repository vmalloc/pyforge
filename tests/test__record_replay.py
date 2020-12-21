from forge import UnexpectedCall, ExpectedEventsNotFound, SignatureException
from .ut_utils import ForgeTestCase

class RecordReplayTest(ForgeTestCase):
    def setUp(self):
        super(RecordReplayTest, self).setUp()
        def some_function(a, b, c):
            raise NotImplementedError()
        self.stub = self.forge.create_function_stub(some_function)
    def tearDown(self):
        self.assertNoMoreCalls()
        super(RecordReplayTest, self).tearDown()

    def test__record_replay_valid(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        self.forge.verify()

    def test__call_counts(self):
        for i in range(2):
            self.stub(1, 2, 3)
            self.stub(1, 2, 3)
        self.assertEqual(self.stub.__forge__.call_count, 0)
        self.forge.replay()
        self.stub(1, 2, 3)
        self.assertEqual(self.stub.__forge__.call_count, 1)
        self.stub(1, 2, 3)
        self.assertEqual(self.stub.__forge__.call_count, 2)
        self.assertIn("2 times", str(self.stub))
        self.forge.reset()
        self.assertEqual(self.stub.__forge__.call_count, 0)

    def test__record_replay_different_not_equal_value(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 6)
        exc = caught.exception
        self.assertEqual(len(exc.expected), 1)
        self.assertEqual(exc.expected[0].args, dict(a=1, b=2, c=3))
        self.assertEqual(exc.got.args, dict(a=1, b=2, c=6))
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_more_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(SignatureException):
            self.stub(1, 2, 3, 4, 5)
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_less_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(SignatureException):
            self.stub()
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_no_actual_call(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.assertExpectedNotMet([self.stub])

    def test__replay_queue_empty(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(1, 2, 3)
        self.assertEqual(caught.exception.expected, [])
        self.assertIs(caught.exception.got.target, self.stub)
        self.assertNoMoreCalls()
        self.forge.verify()
    def test__naming_stubs(self):
        def some_other_function():
            raise NotImplementedError()
        stub2 = self.forge.create_function_stub(some_other_function)
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            stub2()
        exc = caught.exception
        for r in (str, repr):
            self.assertIn('some_function', r(exc.expected))
            self.assertIn('some_other_function', r(exc.got))
        self.assertIn('some_function', str(exc))
        self.assertIn('some_other_function', str(exc))
        self.forge.reset()
    def test__record_self_argument(self):
        def some_func(bla, self, bla2):
            pass
        stub = self.forge.create_function_stub(some_func)
        stub(bla=1, self=2, bla2=3)
        stub(1, 2, 3)
        self.forge.replay()
        stub(bla=1, self=2, bla2=3)
        stub(1, 2, 3)
    def assertExpectedNotMet(self, stubs):
        self.assertGreater(len(stubs), 0)
        with self.assertRaises(ExpectedEventsNotFound) as caught:
            self.forge.verify()
        self.assertEqual(len(caught.exception.events), len(stubs))
        expected = self.forge.queue.get_expected()
        for stub, exception_call in zip(stubs, caught.exception.events):
            expected_call = expected.pop()
            self.assertIs(expected_call, exception_call)
            self.assertIs(expected_call.target, stub)
        self.assertEqual(len(expected), 0)
        self.forge.queue.clear()
