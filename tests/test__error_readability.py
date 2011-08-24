import sys
from difflib import Differ
from types import ModuleType
from contextlib import contextmanager
from .ut_utils import ForgeTestCase
from forge import UnexpectedCall, UnexpectedSetattr

class ErrorClarityTest(ForgeTestCase):
    pass

from forge.exceptions import UNEXPECTED_FUNCTION_CALLED_STR
from forge.exceptions import UNEXPECTED_SETATTR_STR
from forge.exceptions import DIFF_DESCRIPTION_STR

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

    def tearDown(self):
        # ForgeTestCase makes sure no more calls are active etc....
        self.forge.reset()
        super(ErrorsInRegularStubs, self).tearDown()

    def test__function_error_clarity(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCommonCase('some_function'):
            self.stub(1, 2, 4)

    def test__function_error_clarity_no_expected(self):
        self.forge.replay()
        with self.assertUnexpectedEvent("<< None >>",
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
        with self.assertUnexpectedCommonCase('<SomeClass instance>.method'):
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
        record_lineno = self._get_lineno() + 1
        self.stub(1, 2, 3)
        self.forge.replay()
        file_name = __file__
        if file_name.endswith(".pyc"):
            file_name = file_name[:-1]
        replay_lineno = self._get_lineno() + 5
        prologue = "Recorded from %s:%s::test__debug_info" % (file_name, record_lineno)
        prologue += "\nReplayed from %s:%s::test__debug_info" % (file_name, replay_lineno)
        with self.assertUnexpectedCommonCase('some_function',
                                             prologue=prologue):
            self.stub(1, 2, 4)
    def _get_lineno(self):
        return sys._getframe(1).f_lineno
    def test__setattr_clarity(self):
        self.mock.__forge__.expect_setattr('a', 2)
        self.forge.replay()
        with self.assertUnexpectedEvent("setattr(%s, 'a', 2)" % self.mock,
                                        "setattr(%s, 'a', 3)" % self.mock,
                                        message=UNEXPECTED_SETATTR_STR,
                                        cls=UnexpectedSetattr):
            self.mock.a = 3
    def test__identical_expectations_clarity(self):
        wc1 = self.forge.create_wildcard_function_stub()
        wc2 = self.forge.create_wildcard_function_stub()
        wc1()
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            wc2()
        self.assertMultiLineEqual(str(caught.exception),
                                  """%s %s
- <<Wildcard>>()
+ <<Wildcard>>()""" % (UNEXPECTED_FUNCTION_CALLED_STR, DIFF_DESCRIPTION_STR))
    def assertUnexpectedCommonCase(self, function_name, prologue=None):
        return self.assertUnexpectedEvent('%s(a=1, b=2, c=3)' % function_name,
                                         '%s(a=1, b=2, c=4)' % function_name,
                                         prologue=prologue)
    @contextmanager
    def assertUnexpectedEvent(self, expected, found, prologue=None, cls=UnexpectedCall, message=UNEXPECTED_FUNCTION_CALLED_STR):
        diff_str = "%s %s\n" % (message, DIFF_DESCRIPTION_STR)
        if prologue:
            diff_str += prologue
            diff_str += "\n"
        diff_str += "\n".join(map(str.strip, Differ().compare([found], [expected])))
        with self.assertRaises(cls) as caught:
            yield None

        self.assertMultiLineEqual(str(caught.exception),
                                  diff_str)
