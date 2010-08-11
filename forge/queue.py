from contextlib import contextmanager
from collections import deque
from .function_call import FunctionCall
from .exceptions import UnexpectedCall
from .exceptions import ExpectedCallsNotFound
from .utils import renumerate

class ForgeQueue(object):
    def __init__(self, forge):
        super(ForgeQueue, self).__init__()
        self._order_groups = [OrderedGroup()]
        self._forge = forge
    def __len__(self):
        if not self._order_groups:
            return 0
        return sum(len(group) for group in self._order_groups)
    def expect_call(self, target, args, kwargs):
        return self._get_recording_group().expect_call(target, args, kwargs)
    def pop_matching_call(self, target, args, kwargs):
        with self._get_cleanup_context():
            current_group = self._get_replay_group()
            popped = current_group.pop_matching_call(target, args, kwargs)
            if popped is None:
                raise UnexpectedCall(self._get_replay_group().get_expected(), FunctionCall(target, args, kwargs))
            return popped
    @contextmanager
    def _get_cleanup_context(self):
        yield None
        for index, group in renumerate(self._order_groups):
            if group.is_empty() and index != 0:
                self._order_groups.pop(index)
    def pop(self):
        with self._get_cleanup_context():
            return self._get_replay_group().pop()
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
        expected_calls = [call
                          for group in self._order_groups
                          for call in group]
        if expected_calls:
            raise ExpectedCallsNotFound(expected_calls)

class OrderingGroup(object):
    def _append(self, call):
        self._collection.append(call)
    def expect_call(self, target, args, kwargs):
        returned = FunctionCall(target, args, kwargs)
        self._append(returned)
        return returned
    def pop(self):
        return self._collection.pop()
    def pop_matching_call(self, target, args, kwargs):
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
    def pop_matching_call(self, target, args, kwargs):
        if not self._collection:
            return None
        popped = self._collection[0]
        if popped is not None and popped.matches_call(target, args, kwargs):
            return self._collection.popleft()
        return None
    def get_expected(self):
        return self._collection[0] if self._collection else None

class UnorderedGroup(OrderingGroup):
    def __init__(self):
        super(UnorderedGroup, self).__init__()
        self._collection = []
    def pop_matching_call(self, target, args, kwargs):
        for index, expected in enumerate(self._collection):
            if expected.matches_call(target, args, kwargs):
                self._collection.pop(index)
                return expected
        return None
    def get_expected(self):
        return list(self._collection)
