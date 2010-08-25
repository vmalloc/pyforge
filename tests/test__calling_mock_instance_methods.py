import functools
from ut_utils import ForgeTestCase
from ut_utils import Method, ClassMethod, StaticMethod
from ut_utils import build_old_style_class
from ut_utils import build_new_style_class
from ut_utils import resets_forge_at_end
from forge import SignatureException

METHODS = [
    Method('method(self, a, b, c)'),
    ClassMethod('class_method(cls, a, b, c)'),
    StaticMethod('static_method(a, b, c)'),
    Method('without_self()'),
    Method('__len__(self)'),
    ]

MockedNewStyleClass = build_new_style_class(METHODS)
MockedOldStyleClass = build_old_style_class(METHODS)

def for_each_mock(func):
    @functools.wraps(func)
    def newfunc(self, *args, **kwargs):
        for obj in self.mocks:
            func(self, obj, *args, **kwargs)
    return newfunc

class MockInstanceMethodTest(ForgeTestCase):
    def setUp(self):
        super(MockInstanceMethodTest, self).setUp()
        self.newstyle_mock = self.forge.create_mock(MockedNewStyleClass)
        self.oldstyle_mock = self.forge.create_mock(MockedOldStyleClass)
        self.mocks = [self.newstyle_mock, self.oldstyle_mock]
    def test__calling_methods(self):
        self._test__recording_and_calling('method')
    def test__calling_class_methods(self):
        self._test__recording_and_calling('class_method')
    def test__calling_static_methods(self):
        self._test__recording_and_calling('static_method')
    @for_each_mock
    def test__static_method_signature_checking(self, obj):
        with self.assertRaises(SignatureException):
            obj.static_method(1, 2)
        with self.assertRaises(SignatureException):
            obj.static_method()
    @for_each_mock
    def test__class_method_signature_checking(self, obj):
        with self.assertRaises(SignatureException):
            obj.class_method(1, 2, 3, 4)
        with self.assertRaises(SignatureException):
            obj.class_method()

    @for_each_mock
    @resets_forge_at_end
    def _test__recording_and_calling(self, obj, method_name):
        method = getattr(obj, method_name)
        method(1, 2, 3)
        self.forge.replay()
        method(1, 2, 3)
        self.forge.verify()
