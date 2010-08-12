from .stub import FunctionStub
from .queue import ForgeQueue
from .mock_object import MockObject
from .stub_manager import StubManager

class Forge(object):
    def __init__(self):
        super(Forge, self).__init__()
        self.stubs = StubManager(self)
        self.reset()
    def is_replaying(self):
        return self._is_replaying
    def is_recording(self):
        return not self.is_replaying()
    def replay(self):
        self._is_replaying = True
    def reset(self):
        self._is_replaying = False
        self.queue = ForgeQueue(self)
    def pop_expected_call(self):
        return self.queue.pop()
    def verify(self):
        self.queue.verify()

    def create_function_stub(self, func):
        return FunctionStub(self, func)
    def create_method_stub(self, method):
        return FunctionStub(self, method)
    def create_mock(self, mocked_class):
        return MockObject(self, mocked_class)

    def replace_with_stub(self, obj, method_name):
        return self.stubs.replace_with_stub(obj, method_name)
    def restore_all_stubs(self):
        self.stubs.restore_all_stubs()
    def any_order(self):
        return self.queue.get_unordered_group_context()
