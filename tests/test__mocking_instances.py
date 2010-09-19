from numbers import Number
from ut_utils import ForgeTestCase
from forge.mock_handle import MockHandle
from forge import SignatureException
from forge import MockObjectUnhashable
from forge import CannotMockFunctions

class MockedClass(object):
    def some_method(self):
        raise NotImplementedError()

class MockingTest(ForgeTestCase):
    def setUp(self):
        super(MockingTest, self).setUp()
        self.obj = self.forge.create_mock(MockedClass)
    def test__mock_hashability(self):
        self._assert_mock_not_hashable(self.obj)
        self.obj.__forge__.enable_hashing()
        self.assertEquals(id(self.obj), hash(self.obj))
        self.obj.__forge__.disable_hashing()
        self._assert_mock_not_hashable(self.obj)
    def _assert_mock_not_hashable(self, obj):
        with self.assertRaises(MockObjectUnhashable):
            hash(obj)

    def test__mock_object_has_mock_handle(self):
        self.assertIsInstance(self.obj.__forge__, MockHandle)
        self.assertIs(self.obj.__forge__.forge, self.forge)
        self.assertIs(self.obj.__forge__.mock, self.obj)
        self.assertIs(self.obj.__forge__.mocked_class, MockedClass)
        self.assertIsInstance(self.obj.__forge__.id, Number)
    def test__class_attribute(self):
        self.assertIs(self.obj.__class__, MockedClass)
        self.assertIsInstance(self.obj, MockedClass)
        self.assertIsNot(type(self.obj), MockedClass)
    def test__equality(self):
        self.assertTrue(self.obj == self.obj)
        self.assertFalse(self.obj == 2)
        self.assertFalse(self.obj == self.forge.create_mock(MockedClass))
    def test__inequality(self):
        self.assertFalse(self.obj != self.obj)
        self.assertTrue(self.obj != 2)
        self.assertTrue(self.obj != self.forge.create_mock(MockedClass))

class MockingCornerCasesTest(ForgeTestCase):
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(MockingCornerCasesTest, self).tearDown()
    def _test__calling_method_cannot_be_called_bound(self, cls):
        m = self.forge.create_mock(cls)
        #obtaining the method is ok
        method = m.invalid_method
        with self.assertRaises(SignatureException):
            #calling it is not ok
            method()
    def test__calling_new_style_method_cannot_be_called_bound(self):
        class NewStyleClass(object):
            def invalid_method():
                raise NotImplementedError()
        self._test__calling_method_cannot_be_called_bound(NewStyleClass)
    def test__calling_old_style_method_cannot_be_called_bound(self):
        class OldStyleClass:
            def invalid_method():
                raise NotImplementedError()
        self._test__calling_method_cannot_be_called_bound(OldStyleClass)
    def test__mocking_with_method_placeholders(self):
        mock = self.forge.create_mock(dict)
        mock.get(2, 3).and_return(4)
        mock[6].and_return(7)
        with self.assertRaises(AttributeError):
            mock.gettt
        self.forge.replay()
        self.assertEquals(mock.get(2, 3), 4)
        self.assertEquals(mock[6], 7)

class InvalidMockingTest(ForgeTestCase):
    def test__cannot_mock_functions(self):
        for invalid_target in self._get_function_variants():
            with self.assertRaises(CannotMockFunctions):
                self.forge.create_mock(invalid_target)
    def _get_function_variants(self):
        yield lambda *args: None
        yield self._get_function_variants
        def some_function():
            pass
        yield some_function
        yield isinstance
