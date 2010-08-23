from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
from forge.stub_handle import StubHandle

def function():
    "some doc"
    raise NotImplementedError()

class FunctionStubAttributesTest(ForgeTestCase):
    def setUp(self):
        super(FunctionStubAttributesTest, self).setUp()
        self.stub = self.forge.create_function_stub(function)
    def test__name(self):
        self.assertEquals(self.stub.__name__, function.__name__)
    def test__doc(self):
        self.assertEquals(self.stub.__doc__, function.__doc__)
    def test__forge_handle(self):
        stub = FunctionStub(self.forge, function)
        self.assertIs(stub.__forge__.original, function)
        self.assertIs(stub.__forge__.signature.func, function)
        self.assertIsInstance(stub.__forge__, StubHandle)
        self.assertIs(stub.__forge__.stub, stub)
        self.assertIs(stub.__forge__.forge, self.forge)

