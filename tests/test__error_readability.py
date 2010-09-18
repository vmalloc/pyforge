from difflib import Differ
from types import ModuleType
from contextlib import contextmanager
from ut_utils import ForgeTestCase
from forge import UnexpectedCall

class ErrorClarityTest(ForgeTestCase):
    pass

class ErrorsInRegularStubs(ForgeTestCase):
    def setUp(self):
        super(ErrorsInRegularStubs, self).setUp()
        def some_function(a, b, c):
            raise NotImplementedError()
        self.stub = self.forge.create_function_stub(some_function)
        class SomeClass(object):
            def method(self, a, b, c):
                raise NotImplementedError()
            def __call__(self, a, b, c):
                raise NotImplementedError()
            @classmethod
            def class_method(cls, a, b, c):
                raise NotImplementedError()
        self.mock = self.forge.create_mock(SomeClass)
        self.obj = SomeClass()
        self.forge.replace(self.obj, "method")
        self.class_mock = self.forge.create_class_mock(SomeClass)

    def test__function_error_clarity(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase('some_function'):
            self.stub(1, 2, 4)

    def test__function_error_clarity_no_expected(self):
        self.forge.replay()
        with self.assertUnexpectedCall("<< None >>",
                                       "some_function(a=1, b=2, c=4)"):
            self.stub(1, 2, 4)
    def test__method_clarity(self):
        self.mock.method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase("<Mock of 'SomeClass'>.method"):
            self.mock.method(1, 2, 4)
    def test__method_of_object_with_different_name_for_self(self):
        class SomeClass(object):
            def method(not_self, a, b, c):
                raise NotImplementedError()
        mock = self.forge.create_mock(SomeClass)
        mock.method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase("<Mock of 'SomeClass'>.method"):
            mock.method(1, 2, 4)
    def test__class_method_clarity(self):
        self.mock.class_method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase("<Mock of 'SomeClass'>.class_method"):
            self.mock.class_method(1, 2, 4)
    def test__object_calling_clarity(self):
        self.mock(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase("<Mock of 'SomeClass'>.__call__"):
            self.mock(1, 2, 4)
    def test__replaced_method_clarity(self):
        self.obj.method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase('%s.method' % self.obj):
            self.obj.method(1, 2, 4)
    def test__replaced_module_clarity(self):
        module_name = 'some_module_name'
        module = ModuleType(module_name)
        def f(a, b, c):
            raise NotImplementedError()
        module.f = f
        self.forge.replace(module, 'f')
        module.f(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase('%s.f' % module_name):
            module.f(1, 2, 4)
    def test__debug_info(self):
        self.forge.debug.enable()
        self.stub(1, 2, 3)
        self.forge.replay()
        file_name = __file__
        if file_name.endswith(".pyc"):
            file_name = file_name[:-1]
        prologue = "Recorded from %s:82::test__debug_info" % file_name
        prologue += "\nReplayed from %s:91::test__debug_info" % file_name
        with self.assertUnexpectedCommonCase('some_function',
                                             prologue=prologue):
            self.stub(1, 2, 4)
    def assertUnexpectedCommonCase(self, function_name, prologue=None):
        return self.assertUnexpectedCall('%s(a=1, b=2, c=3)' % function_name,
                                         '%s(a=1, b=2, c=4)' % function_name,
                                         prologue=prologue)
    @contextmanager
    def assertUnexpectedCall(self, expected, found, prologue=None):
        diff_str = "Unexpected function called! (Expected: +, Got: -)\n"
        if prologue:
            diff_str += prologue
            diff_str += "\n"
        diff_str += "\n".join(map(str.strip, Differ().compare([found], [expected])))
        with self.assertRaises(UnexpectedCall) as caught:
            yield None

        self.assertMultiLineEqual(str(caught.exception),
                                  diff_str)
