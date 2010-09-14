import itertools
from contextlib import contextmanager
from .stub import FunctionStub
from .queue import ForgeQueue
from .class_mock import ClassMockObject
from .wildcard_mock_object import WildcardMockObject
from .replacer import Replacer
from .stub_manager import StubManager
from .attribute_manager import AttributeManager
from .sentinel import Sentinel
from .dtypes import WILDCARD_FUNCTION

class Forge(object):
    def __init__(self):
        super(Forge, self).__init__()
        self.replacer = Replacer(self)
        self.reset()
        self._id_allocator = itertools.count()
    def get_new_handle_id(self):
        return self._id_allocator.next()
    def is_replaying(self):
        return self._is_replaying
    def is_recording(self):
        return not self.is_replaying()
    def replay(self):
        self._is_replaying = True
    def reset(self):
        self._is_replaying = False
        self.queue = ForgeQueue(self)
        self.stubs = StubManager(self)
        self.attributes = AttributeManager(self)
    @contextmanager
    def verified_replay_context(self):
        self.replay()
        yield
        self.verify()
        self.reset()
    def pop_expected_call(self):
        return self.queue.pop()
    def verify(self):
        self.queue.verify()

    def create_function_stub(self, func, name=None):
        return FunctionStub(self, func, name=name)
    def create_wildcard_function_stub(self):
        return self.create_function_stub(WILDCARD_FUNCTION)
    def create_method_stub(self, method, name=None):
        return FunctionStub(self, method, name=name)
    def create_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=True, hybrid=False)
    def create_hybrid_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=True, hybrid=True)
    def create_class_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=False, hybrid=False)
    def create_wildcard_mock(self):
        return WildcardMockObject(self)
    def create_sentinel(self, name=None):
        return Sentinel(name)
    def replace(self, obj, attr_name):
        return self.replacer.replace(obj, attr_name)
    def replace_many(self, obj, *attr_names):
        return [self.replace(obj, attr_name) for attr_name in attr_names]
    def replace_with(self, obj, attr_name, replacement):
        return self.replacer.replace_with(obj, attr_name, replacement)
    def restore_all_replacements(self):
        self.replacer.restore_all()
    def any_order(self):
        return self.queue.get_unordered_group_context()
