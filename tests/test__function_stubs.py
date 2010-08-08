from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
from forge import UnexpectedCall
from forge import ExpectedCallsNotFound
from forge import SignatureException

def _func1(a, b, c=2):
    raise NotImplementedError()

def _func2(a, b, c=2, *args, **kwargs):
    raise NotImplementedError()

class FunctionStubAttributesTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubAttributesTest, self).setUp()
        self.stub = self.forge.create_function_stub(_func2)
    def test__name(self):
        self.assertEquals(self.stub.__name__, _func2.__name__)
    def test__doc(self):
        self.assertEquals(self.stub.__doc__, _func2.__doc__)

class FunctionStubInitializationTest(ForgeTestCase):
    def test__initialization(self):
        obj = object()
        stub = FunctionStub(self.forge, _func1, obj=obj)
        self.assertIs(stub._obj, obj)
        self.assertIs(stub._original, _func1)
        self.assertIs(stub._signature.func, _func1)
    
    def test__without_obj(self):
        stub = FunctionStub(self.forge, _func1)
        self.assertIsNone(stub._obj)

class FunctionStubRecordTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubRecordTest, self).setUp()
        def _f():
            raise NotImplementedError()
        self.stub = FunctionStub(self.forge, _f)
    def test__record_invalid_arguments(self):
        args = (1, 2, 3)
        kwargs = dict(a=2, b=3, c=4)
        expected_failure = SignatureException()
        def _fake_get_normalized_args(given_args, given_kwargs):
            self.assertEquals(given_args, args)
            self.assertEquals(given_kwargs, kwargs)
            raise expected_failure
        self.stub._signature.get_normalized_args = _fake_get_normalized_args
        with self.assertRaises(SignatureException) as caught:
            self.stub(*args, **kwargs)
        self.assertIs(caught.exception, expected_failure)
        self.assertEquals(len(self.forge.queue), 0)
    def test__record_valid_arguments(self):
        args = (1, 2, 3)
        kwargs = dict(a=2)
        normalized_args = dict(some_key=1, some_other_key=2)
        def _fake_get_normalized_args(given_args, given_kwargs):
            self.assertEquals(given_args, args)
            self.assertEquals(given_kwargs, kwargs)
            return normalized_args
        self.stub._signature.get_normalized_args = _fake_get_normalized_args
        self.stub(*args, **kwargs)
        self.assertEquals(len(self.forge.queue), 1)
        expected_call = self.forge.queue._queue[0]
        self.assertIs(expected_call.target, self.stub)
        self.assertIs(expected_call.args, normalized_args)
        
class FunctionStubReplayTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubReplayTest, self).setUp()
        self.stub = FunctionStub(self.forge, lambda *args, **kwargs: None)
    def test__record_replay_valid(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.stub(1, 2, 3)
        self.forge.verify()
    def test__record_replay_different(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:            
            self.stub(1, 2, 6)
        exc = caught.exception
        self.assertEquals(exc.expected.args, {0:1, 1:2, 2:3})
        self.assertEquals(exc.got.args, {0:1, 1:2, 2:6})
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_more_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:            
            self.stub(1, 2, 3, 4, 5)
        exc = caught.exception
        self.assertEquals(exc.expected.args, {0:1, 1:2, 2:3})
        self.assertEquals(exc.got.args, {0:1, 1:2, 2:3, 3:4, 4:5})
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_different_less_args(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:            
            self.stub()
        exc = caught.exception
        self.assertEquals(exc.expected.args, {0:1, 1:2, 2:3})
        self.assertEquals(exc.got.args, {})
        self.assertExpectedNotMet([self.stub])
    def test__record_replay_no_actual_call(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        self.assertExpectedNotMet([self.stub])            
    def assertExpectedNotMet(self, stubs):
        for stub in stubs:
            expected_call = self.forge.queue._queue.pop()
            self.assertIs(expected_call.target, stub)
        self.assertEquals(len(self.forge.queue), 0)
