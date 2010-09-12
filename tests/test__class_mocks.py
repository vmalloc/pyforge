from ut_utils import *
from forge import SignatureException

METHODS = [
    ClassMethod('class_method(cls, a, b, c, d=5)'),
    StaticMethod('static_method(a, b, c, d=5)'),
    Method('regular_method(self, a, b, c, d=5)'),
    ]

class _ClassMockTest(ForgeTestCase):
    def setUp(self):
        super(_ClassMockTest, self).setUp()
        factory = self._get_class_factory()
        methods = self._get_methods()
        self.mocked_class = factory(methods)
        self.mock = self.forge.create_class_mock(self.mocked_class)
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(_ClassMockTest, self).tearDown()

class _OldStyleTest(object):
    def _get_class_factory(self):
        return build_old_style_class
class _NewStyleTest(object):
    def _get_class_factory(Self):
        return build_new_style_class

class _BasicClassMockTest(_ClassMockTest):
    def _get_methods(self):
        return METHODS
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

class OldStyleBasicTest(_BasicClassMockTest, _OldStyleTest):
    pass
class NewStyleBasicTest(_BasicClassMockTest, _NewStyleTest):
    pass


class ClassMockConstructionTest(ForgeTestCase):
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(ClassMockConstructionTest, self).tearDown()
    def test__empty_constructor_new_style(self):
        class MyClass(object):
            def __init__(self):
                pass
        self._test__empty_construction(MyClass)
    def test__empty_constructor_old_style(self):
        class MyClass:
            def __init__(self):
                pass
        self._test__empty_construction(MyClass)
    def test__no_constructor_new_style(self):
        class MyClass(object):
            pass
        self._test__empty_construction(MyClass)
    def test__no_constructor_old_style(self):
        class MyClass:
            pass
        self._test__empty_construction(MyClass)
    def _test__empty_construction(self, cls):
        mock = self.forge.create_class_mock(cls)
        with self.assertRaises(SignatureException):
            mock(1, 2, 3)
        with self.assertRaises(SignatureException):
            mock(1)
        result = self.forge.create_mock(cls)
        mock().and_return(result)
        self.forge.replay()
        self.assertIs(result, mock())
    def test__construction_new_style(self):
        class MyClass(object):
            def __init__(self, a, b, c, d=4):
                pass
        self._test__construction(MyClass)
    def test__construction_old_style(self):
        class MyClass:
            def __init__(self, a, b, c, d=4):
                pass
        self._test__construction(MyClass)
    def test__construction_inheritence_new_style(self):
        class MyClass(object):
            def __init__(self, a, b, c, d=4):
                pass
        class MyClass2(MyClass):
            pass
        self._test__construction(MyClass2)
    def test__construction_inheritence_old_style(self):
        class MyClass:
            def __init__(self, a, b, c, d=4):
                pass
        class MyClass2(MyClass):
            pass
        self._test__construction(MyClass2)
    def test__construction_with_call_operator_new_style(self):
        class MyClass(object):
            def __init__(self, a, b, c, d=4):
                pass
            def __call__(self, a, b):
                pass
        self._test__construction(MyClass)
    def test__construction_with_call_operator_old_style(self):
        class MyClass:
            def __init__(self, a, b, c, d=4):
                pass
            def __call__(self, a, b):
                pass
        self._test__construction(MyClass)
    def _test__construction(self, cls):
        mock = self.forge.create_class_mock(cls)
        with self.assertRaises(SignatureException):
            mock()
        with self.assertRaises(SignatureException):
            mock(1, 2)
        with self.assertRaises(SignatureException):
            mock(1, e=100)
        result_1 = self.forge.create_mock(cls)
        mock(1, 2, 3).and_return(result_1)
        result_2 = self.forge.create_mock(cls)
        mock(1, 2, 3, 4).and_return(result_2)
        self.forge.replay()
        self.assertIs(result_1, mock(1, 2, 3))
        self.assertIs(result_2, mock(1, 2, 3, 4))




