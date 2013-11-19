import itertools
import time
from contextlib import contextmanager
from .python3_compat import iteritems
from .stub import FunctionStub
from .queue import ForgeQueue
from .class_mock import ClassMockObject
from .wildcard_mock_object import WildcardMockObject
from .replacer import Replacer
from .stub_manager import StubManager
from .attribute_manager import AttributeManager
from .sentinel import Sentinel
from .dtypes import WILDCARD_FUNCTION
from .debug import ForgeDebug


class Forge(object):
    def __init__(self):
        super(Forge, self).__init__()
        self.replacer = Replacer(self)
        self.attributes = AttributeManager(self)
        self.reset()
        self._id_allocator = itertools.count()
        self.debug = ForgeDebug(self)

    def get_new_handle_id(self):
        return next(self._id_allocator)

    def is_replaying(self):
        return self._is_replaying

    def is_recording(self):
        return not self.is_replaying()

    def replay(self):
        self._is_replaying = True

    def reset(self):
        self._is_replaying = False
        self.session_id = time.time()
        self.queue = ForgeQueue(self)
        self.stubs = StubManager(self)
        self.attributes.reset_replay_attributes()

    @contextmanager
    def record_context(self):
        assert self.is_recording()
        yield

    @contextmanager
    def verified_replay_context(self):
        self.replay()
        yield
        self.verify()
        self.reset()

    def verify(self):
        self.queue.verify()

    def create_function_stub(self, func, name=None):
        return FunctionStub(self, func, name=name)

    def create_wildcard_function_stub(self, name=None):
        return self.create_function_stub(WILDCARD_FUNCTION, name=name)

    def create_method_stub(self, method, name=None):
        return FunctionStub(self, method, name=name)

    def create_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=True, hybrid=False)

    def create_hybrid_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=True, hybrid=True)

    def create_class_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=False, hybrid=False)

    def create_hybrid_class_mock(self, mocked_class):
        return ClassMockObject(self, mocked_class, behave_as_instance=False, hybrid=True)

    def create_wildcard_mock(self, name=None):
        return WildcardMockObject(self, name=name)
    # arguments decorated to avoid conflicts with attrs

    def create_sentinel(__forge__self, __forge__name=None, **attrs):
        return Sentinel(__forge__name, **attrs)

    def create_mock_with_attrs(self, mocked_class, **attrs):
        returned = self.create_mock(mocked_class)
        for attr, value in iteritems(attrs):
            setattr(returned, attr, value)
        return returned

    def replace(self, obj, attr_name):
        return self.replacer.replace(obj, attr_name)

    def replacing_context(self, obj, attr_name):
        return self.replacer.replacing_context(obj, attr_name)

    def replace_many(self, obj, *attr_names):
        return [self.replace(obj, attr_name) for attr_name in attr_names]

    def replace_with(self, obj, attr_name, replacement):
        return self.replacer.replace_with(obj, attr_name, replacement)

    def restore_all_replacements(self):
        self.replacer.restore_all()

    def any_order(self):
        return self.queue.get_any_order_group_context()

    def ordered(self):
        return self.queue.get_ordered_group_context()

    def interleaved_order(self):
        return self.queue.get_interleaved_group_context()

    group = ordered
