from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
from forge.stub_handle import StubHandle

def some_function():
    "some doc"
    raise NotImplementedError()

class FunctionStubAttributesTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubAttributesTest, self).setUp()
        self.stub = self.forge.create_function_stub(some_function)
    def test__name(self):
        self.assertEquals(self.stub.__name__, some_function.__name__)
    def test__doc(self):
        self.assertEquals(self.stub.__doc__, some_function.__doc__)
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

