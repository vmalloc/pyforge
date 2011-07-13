from contextlib import contextmanager
from collections import deque
from .function_call import FunctionCall
from .setattr import Setattr
from .exceptions import UnexpectedCall
from .exceptions import UnexpectedSetattr
from .exceptions import ExpectedEventsNotFound
from .utils import renumerate

class ForgeQueue(object):
    def __init__(self, forge):
        super(ForgeQueue, self).__init__()
        self._order_groups = [OrderedGroup()]
        self._whenever = set()
        self._forge = forge
    def __len__(self):
        if not self._order_groups:
            return 0
        return sum(len(group) for group in self._order_groups)
    def allow_whenever(self, queued_object):
        self._whenever.add(queued_object)
    def push_call(self, target, args, kwargs, caller_info):
        return self._push(FunctionCall(target, args, kwargs, caller_info))
    def push_setattr(self, target, name, value, caller_info):
        return self._push(Setattr(target, name, value, caller_info))
    def pop_matching_call(self, target, args, kwargs, caller_info):
        return self._pop_matching(FunctionCall(target, args, kwargs, caller_info), UnexpectedCall)
    def pop_matching_setattr(self, target, name, value, caller_info):
        return self._pop_matching(Setattr(target, name, value, caller_info), UnexpectedSetattr)
    def _push(self, queued_object):
        return self._get_recording_group().push(queued_object)
    def _pop_matching(self, queued_object, unexpected_class):
        with self._get_cleanup_context():
            current_group = self._get_replay_group()
            popped = current_group.pop_matching(queued_object)
            if popped is None:
                popped = self._find_whenever_object(queued_object)
            if popped is None:
                raise unexpected_class(self._get_replay_group().get_expected(), queued_object)
            return popped
    def _find_whenever_object(self, queued_object):
        for w in self._whenever:
            if w.matches(queued_object):
                return w
        return None
    def pop(self):
        return self._get_recording_group().pop()
    def get_expected(self):
        return self._get_replay_group().get_expected()
    @contextmanager
    def _get_cleanup_context(self):
        yield None
        for index, group in renumerate(self._order_groups):
            if group.is_empty() and index != 0:
                self._order_groups.pop(index)
    def _get_recording_group(self):
        return self._order_groups[-1]
    def _get_replay_group(self):
        for order_group in self._order_groups:
            if not order_group.is_empty():
                return order_group
        return self._order_groups[0]
    @contextmanager
    def get_unordered_group_context(self):
        self._order_groups.append(UnorderedGroup())
        yield
        self._order_groups.append(OrderedGroup())
    def verify(self):
        expected_events = [event
                           for group in self._order_groups
                           for event in group]
        if expected_events:
            raise ExpectedEventsNotFound(expected_events)

class OrderingGroup(object):
    def push(self, obj):
        self._collection.append(obj)
        return obj
    def pop(self):
        return self._collection.pop()
    def pop_matching(self, obj):
        raise NotImplementedError()
    def get_expected(self):
        raise NotImplementedError()
    def __iter__(self):
        return iter(self._collection)
    def __len__(self):
        return len(self._collection)
    def is_empty(self):
        return len(self) == 0

class OrderedGroup(OrderingGroup):
    def __init__(self):
        super(OrderedGroup, self).__init__()
        self._collection = deque()
    def pop_matching(self, obj):
        if not self._collection:
            return None
        popped = self._collection[0]
        if popped is not None and popped.matches(obj):
            return self._collection.popleft()
        return None
    def get_expected(self):
        return self._collection[0] if self._collection else None

class UnorderedGroup(OrderingGroup):
    def __init__(self):
        super(UnorderedGroup, self).__init__()
        self._collection = []
    def pop_matching(self, obj):
        for index, expected in enumerate(self._collection):
            if expected.matches(obj):
                self._collection.pop(index)
                return expected
        return None
    def get_expected(self):
        return list(self._collection)
