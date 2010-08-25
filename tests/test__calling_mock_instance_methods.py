from ut_utils import ForgeTestCase
from forge import SignatureException

class MockedOldStyleClass:
    def method(self, a, b, c):
        raise NotImplementedError()
    @classmethod
    def class_method(cls, a, b, c):
        raise NotImplementedError()
    @staticmethod
    def static_method(a, b, c):
        raise NotImplementedError()
    def without_self():
        raise NotImplementedError()
class MockedNewStyleClass(object):
    def method(self, a, b, c):
        raise NotImplementedError()
    @classmethod
    def class_method(cls, a, b, c):
        raise NotImplementedError()
    @staticmethod
    def static_method(a, b, c):
        raise NotImplementedError()
    def without_self():
        raise NotImplementedError()

class MockInstanceMethodTest(ForgeTestCase):
    def setUp(self):
        super(MockInstanceMethodTest, self).setUp()
        self.newstyle_mock = self.forge.create_mock(MockedNewStyleClass)
        self.oldstyle_mock = self.forge.create_mock(MockedOldStyleClass)
    def test__calling_methods(self):
        self._test__recording_and_calling('method')
    def test__calling_class_methods(self):
        self._test__recording_and_calling('class_method')
    def test__calling_static_methods(self):
        self._test__recording_and_calling('static_method')
    def test__static_method_signature_checking(self):
        for obj in (self.newstyle_mock, self.oldstyle_mock):
            with self.assertRaises(SignatureException):
                obj.static_method(1, 2)
            with self.assertRaises(SignatureException):
                obj.static_method()
    def test__class_method_signature_checking(self):
        for obj in (self.newstyle_mock, self.oldstyle_mock):
            with self.assertRaises(SignatureException):
                obj.class_method(1, 2, 3, 4)
            with self.assertRaises(SignatureException):
                obj.class_method()

    def _test__recording_and_calling(self, method_name):
        for obj in (self.newstyle_mock, self.oldstyle_mock):
            method = getattr(obj, method_name)
            method(1, 2, 3)
            self.forge.replay()
            method(1, 2, 3)
            self.forge.verify()
            self.assertNoMoreCalls()
            self.forge.reset()

