from ut_utils import *
from forge import SignatureException

METHODS = [
    ClassMethod('class_method(cls, a, b, c, d=5)'),
    StaticMethod('static_method(a, b, c, d=5)'),
    Method('regular_method(self, a, b, c, d=5)'),
    Method('__init__(self, a, b, c, d=5)'),
    Method('__call__(self, a, b)'),
    ]

class _ClassMocksTest(ForgeTestCase):
    def setUp(self):
        super(_ClassMocksTest, self).setUp()
        self.mocked_class = self._get_class()
        self.mock = self.forge.create_class_mock(self.mocked_class)
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(_ClassMocksTest, self).tearDown()
    def test__isinstance(self):
        self.assertFalse(isinstance(self.mock, self.mocked_class))
        self.assertTrue(isinstance(self.mock, type(self.mocked_class)))
    def test__class_methods_can_be_called(self):
        self.mock.class_method(1, 2, 3)
        self.forge.replay()
        self.mock.class_method(1, 2, 3)
    def test__static_methods_can_be_called(self):
        self.mock.static_method(1, 2, 3)
        self.forge.replay()
        self.mock.static_method(1, 2, 3)
    def test__class_and_static_methods_signature_checks(self):
        for meth in (self.mock.class_method, self.mock.static_method):
            with self.assertRaises(SignatureException):
                meth()
            with self.assertRaises(SignatureException):
                meth(1, 2, 3, 4, 5)
            with self.assertRaises(SignatureException):
                meth(1, 2, 3, e=5)
    def test__regular_methods_calling(self):
        fake_self = object()
        with self.assertRaises(SignatureException):
            self.mock.regular_method(1, 2, 3)
        self.mock.regular_method(fake_self, 1, 2, 3)
        self.mock.regular_method(fake_self, 1, 2, 3, d=19)
        self.forge.replay()
        self.mock.regular_method(fake_self, 1, 2, 3)
        self.mock.regular_method(fake_self, 1, 2, 3, d=19)
    def test__regular_methods_calling_signature_check(self):
        with self.assertRaises(SignatureException):
            self.mock.regular_method(1, 2, 3)
        with self.assertRaises(SignatureException):
            self.mock.regular_method()
        with self.assertRaises(SignatureException):
            self.mock.regular_method(1, 2)
        with self.assertRaises(SignatureException):
            self.mock.regular_method(d=10)
    def test__construction(self):
        with self.assertRaises(SignatureException):
            self.mock(1, 2) # should fail although the __call__ method accepts this signature!
        instance1 = object()
        instance2 = object()
        self.mock(1, 2, 3).and_return(instance1)
        self.mock(1, 2, 3, 4).and_return(instance2)
        self.forge.replay()
        self.assertIs(self.mock(1, 2, 3), instance1)
        self.assertIs(self.mock(1, 2, 3, 4), instance2)

class NewStyleClassMocksTest(_ClassMocksTest):
    def _get_class(self):
        return build_new_style_class(METHODS)
class OldStyleClassMocksTest(_ClassMocksTest):
    def _get_class(self):
        return build_old_style_class(METHODS)
