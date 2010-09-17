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
        self.forge.replace(self.obj, 'method')
        self.class_mock = self.forge.create_class_mock(SomeClass)
    @contextmanager
    def assertUnexpectedCall(self, diff_str):
        with self.assertRaises(UnexpectedCall) as caught:
            yield None
        diff_str = "Unexpected function called! (Expected: +, Got: -)\n" + diff_str.lstrip()
        self.assertMultiLineEqual(str(caught.exception),
                                  diff_str)

    def test__function_error_clarity(self):
        self.stub(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedCall("""
- some_function(a=1, b=2, c=4)
?                           ^
+ some_function(a=1, b=2, c=3)
?                           ^"""):
            self.stub(1, 2, 4)

    def test__function_error_clarity_no_expected(self):
        self.forge.replay()
        with self.assertUnexpectedCall("""
- some_function(a=1, b=2, c=4)
+ << None >>"""):
            self.stub(1, 2, 4)
    def test__method_clarity(self):
        self.mock.method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedMethodCall('method'):
            self.mock.method(1, 2, 4)
    def test__method_of_object_with_different_name_for_self(self):
        class SomeClass(object):
            def method(not_self, a, b, c):
                raise NotImplementedError()
        mock = self.forge.create_mock(SomeClass)
        mock.method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedMethodCall('method'):
            mock.method(1, 2, 4)
    def test__class_method_clarity(self):
        self.mock.class_method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedMethodCall('class_method'):
            self.mock.class_method(1, 2, 4)
    def test__object_calling_clarity(self):
        self.mock(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedMethodCall('__call__'):
            self.mock(1, 2, 4)
    def test__replaced_method_clarity(self):
        self.obj.method(1, 2, 3)
        self.forge.replay()
        with self.assertUnexpectedMethodCall('method', str(self.obj)):
            self.obj.method(1, 2, 4)
    def assertUnexpectedMethodCall(self, method_name, obj_name="<Mock of 'SomeClass'>"):
        spaces = (len(method_name) + len(obj_name)) * " "
        return self.assertUnexpectedCall("""
- %s.%s(a=1, b=2, c=4)
? %s              ^
+ %s.%s(a=1, b=2, c=3)
? %s              ^""" % ((obj_name, method_name, spaces) * 2))
