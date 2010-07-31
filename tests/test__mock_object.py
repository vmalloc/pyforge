from ut_utils import TestCase
from forge import Forge
from forge.mock_object import MockObject
from forge.mock_handle import MockHandle

class MockObjectTest(TestCase):
    def setUp(self):
        super(MockObjectTest, self).setUp()
        self.forge = Forge()
        self.obj =MockObject(self.forge)
    def test__mock_object_has_mock_manager(self):
        self.assertIsInstance(self.obj.__forge__, MockHandle)
        self.assertIs(self.obj.__forge__.forge, self.forge)
        self.assertIs(self.obj.__forge__.mock, self.obj)
    def test__setting_mock_object_attributes(self):
        attr_value = self.obj.a = object()
        self.assertIs(self.obj.a, attr_value)
        self.forge.replay()
        self.assertIs(self.obj.a, attr_value)
    def test__getattr_of_nonexisting_attr_during_replay(self):
        self.forge.replay()
        with self.assertRaises(AttributeError):
            value = self.obj.nonexisting_attr

        
