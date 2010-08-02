from ut_utils import ForgeTestCase
from forge.mock_handle import MockHandle
from forge import UnexpectedCall, UnauthorizedMemberAccess

class MockedClass(object):
    def method_no_args(self):
        raise NotImplementedError()
    def method_args(self, a, b, c):
        raise NotImplementedError()
    def method_args_and_defaults(self, a, b, c=2):
        raise NotImplementedError()
    def method_varargs(self, a, *args):
        raise NotImplementedError()
    def method_kwargs(self, a, **kwargs):
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
            self.obj.method_args_and_defaults

    def test__record_replay_regular_methods(self):
        self.obj.method_args_and_defaults(1, 2, 3)
        self.forge.replay()
        self.obj.method_args_and_defaults(1, 2, 3)
        self.forge.verify()
    def test__record_replay_missing_record(self):
        self.forge.replay()
        with self.assertRaises(UnauthorizedMemberAccess) as caught:
            self.obj.method_args_and_defaults
        exc = caught.exception
        self.assertIs(exc.object, self.obj)
        self.assertEquals(exc.attribute, "method_args_and_defaults")
        
