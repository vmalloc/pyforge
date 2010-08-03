from ut_utils import ForgeTestCase
from forge.mock_handle import MockHandle
from forge import UnexpectedCall, UnauthorizedMemberAccess, SignatureException

class MockedClass(object):
    def method_without_self():
        raise NotImplementedError()
    def regular_method(self, a, b, c=2, *args, **kwargs):
        raise NotImplementedError()
    def regular_method_without_args(self):
        raise NotImplementedError()

class MockingTest(ForgeTestCase):
    def setUp(self):
        super(MockingTest, self).setUp()
        self.obj = self.forge.create_mock(MockedClass)
    def test__mock_object_has_mock_handle(self):
        self.assertIsInstance(self.obj.__forge__, MockHandle)
        self.assertIs(self.obj.__forge__.forge, self.forge)
        self.assertIs(self.obj.__forge__.mock, self.obj)
        self.assertIs(self.obj.__forge__.mocked_class, MockedClass)
    def test__class_attribute(self):
        self.assertIs(self.obj.__class__, MockedClass)
        self.assertIsInstance(self.obj, MockedClass)
        self.assertIsNot(type(self.obj), MockedClass)
    def test__setting_mock_object_attributes(self):
        attr_value = self.obj.a = object()
        self.assertIs(self.obj.a, attr_value)
        self.forge.replay()
        self.assertIs(self.obj.a, attr_value)
    def test__getattr_of_nonexisting_attr_during_replay(self):
        self.forge.replay()
        with self.assertRaises(AttributeError):
            value = self.obj.nonexisting_attr

        with self.assertRaises(AttributeError):
            # a private case of the above, just making a point
            value = self.obj.nonexisting_method()
    def test__getattr_of_methods_during_replay(self):
        self.forge.replay()
        with self.assertRaises(UnauthorizedMemberAccess):
            self.obj.regular_method

    def test__record_replay_regular_methods(self):
        self.obj.regular_method(1, 2, 3)
        self.forge.replay()
        self.obj.regular_method(1, 2, 3)
        self.forge.verify()
    def test__record_method_invalid_args(self):
        with self.assertRaises(SignatureException):
            self.obj.regular_method()
        with self.assertRaises(SignatureException):
            self.obj.regular_method_without_args(1)
    def test__record_method_invalid_method(self):
        with self.assertRaises(SignatureException):
            self.obj.method_without_self()
    def test__record_replay_missing_record(self):
        self.forge.replay()
        with self.assertRaises(UnauthorizedMemberAccess) as caught:
            self.obj.regular_method
        exc = caught.exception
        self.assertIs(exc.object, self.obj)
        self.assertEquals(exc.attribute, "regular_method")
    def test__record_replay_unexpected_call(self):
        self.obj.regular_method(1, 2, 3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.obj.regular_method(1, 2, 3, 4)
        self.assertIs(caught.exception.expected.target, self.obj.regular_method)
        self.assertIs(caught.exception.got.target, self.obj.regular_method)
        
