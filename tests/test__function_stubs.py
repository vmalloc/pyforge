from numbers import Number
from .ut_utils import ForgeTestCase
from forge.stub import FunctionStub
from forge.stub_handle import StubHandle

from urllib.request import urlopen

def some_function():
    "some doc"
    raise NotImplementedError()

class FunctionStubbingTest(ForgeTestCase):
    def test__stubbing_urlopen(self):
        # known bug in python 3
        urlopen_stub = self.forge.create_function_stub(urlopen)
        urlopen_stub("url").and_return(666)
        self.forge.replay()
        self.assertEqual(urlopen_stub("url"), 666)

class FunctionStubAttributesTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubAttributesTest, self).setUp()
        self.stub = self.forge.create_function_stub(some_function)
    def test__name(self):
        self.assertEqual(self.stub.__name__, some_function.__name__)
    def test__specific_name(self):
        stub = self.forge.create_function_stub(some_function, name='other_name')
        self.assertEqual(stub.__name__, 'other_name')
    def test__doc(self):
        self.assertEqual(self.stub.__doc__, some_function.__doc__)
    def test__stub_id(self):
        self.assertIsInstance(self.stub.__forge__.id, Number)
    def test__str_repr(self):
        self.assertIn('some_function', str(self.stub))
        self.assertIn('some_function', repr(self.stub))
    def test__forge_handle(self):
        stub = FunctionStub(self.forge, some_function)
        self.assertIs(stub.__forge__.original, some_function)
        self.assertIs(stub.__forge__.signature.func, some_function)
        self.assertIsInstance(stub.__forge__, StubHandle)
        self.assertIs(stub.__forge__.stub, stub)
        self.assertIs(stub.__forge__.forge, self.forge)
    def test__stub_record_marker(self):
        stub = FunctionStub(self.forge, some_function)
        self.assertFalse(stub.__forge__.has_recorded_calls())
        stub()
        self.assertTrue(stub.__forge__.has_recorded_calls())
        self.forge.replay()
        stub()
        self.assertTrue(stub.__forge__.has_recorded_calls())
        self.forge.verify()
        self.assertTrue(stub.__forge__.has_recorded_calls())
        self.forge.reset()
        self.assertFalse(stub.__forge__.has_recorded_calls())
