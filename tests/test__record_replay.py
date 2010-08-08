from ut_utils import ForgeTestCase
from forge import UnexpectedCall, SignatureException, UnauthorizedMemberAccess

class MockedNewStyleClass(object):
    def method_without_self():
        raise NotImplementedError()
    def regular_method(self, a, b, c=2, *args, **kwargs):
        raise NotImplementedError()
    def regular_method_without_args(self):
        raise NotImplementedError()
    

class MockedOldStyleClass:
    def method_without_self():
        raise NotImplementedError()
    def regular_method(self, a, b, c=2, *args, **kwargs):
        raise NotImplementedError()
    def regular_method_without_args(self):
        raise NotImplementedError()

class _MockRecordReplayTest(ForgeTestCase):
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

class NewStyleClassMockRecordReplayTest(_MockRecordReplayTest):
    def setUp(self):
        super(NewStyleClassMockRecordReplayTest, self).setUp()
        self.obj = self.forge.create_mock(MockedNewStyleClass)
class OldStyleClassMockRecordReplayTest(_MockRecordReplayTest):
    def setUp(self):
        super(OldStyleClassMockRecordReplayTest, self).setUp()
        self.obj = self.forge.create_mock(MockedOldStyleClass)
