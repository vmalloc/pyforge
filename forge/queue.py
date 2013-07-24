import sys
import traceback
import logging
from contextlib import contextmanager

from .function_call import FunctionCall
from .setattr import Setattr
from .exceptions import UnexpectedCall, UnexpectedSetattr, ExpectedEventsNotFound
from .queued_node import QueuedNode
from .queued_group import OrderedGroup, AnyOrderGroup, InterleavedGroup

_logger = logging.getLogger("pyforge")


class WheneverDecorator(QueuedNode):
    def __init__(self, obj):
        super(WheneverDecorator, self).__init__()
        self.obj = obj

    def get_expected(self):
        return []

    def get_available(self):
        return [self.obj]

    def pop_matching(self, queue_object):
        return self.obj if self.obj.matches(queue_object) else None

    def __len__(self):
        return len(self.obj)

    def __repr__(self):
        return "<whenever %s>" % (repr(self.obj),)


class ForgeQueue(object):
    def __init__(self, forge):
        super(ForgeQueue, self).__init__()
        self._root_group = OrderedGroup()
        self._recording_group = self._root_group
        self._forge = forge

    def get_expected(self):
        return self._root_group.get_expected()

    def get_available(self):
        return self._root_group.get_available()

    def is_empty(self):
        return not self._root_group.get_expected()

    def __len__(self):
        return len(self._root_group)

    def clear(self):
        self._root_group = OrderedGroup()
        self._recording_group = self._root_group

    def allow_whenever(self, queued_object):
        queued_object.get_parent().discard_child(queued_object)
        self._recording_group.push_out_of_band(WheneverDecorator(queued_object))

    def push_call(self, target, args, kwargs, caller_info):
        return self._push(FunctionCall(target, args, kwargs, caller_info))

    def push_setattr(self, target, name, value, caller_info):
        return self._push(Setattr(target, name, value, caller_info))

    def pop_matching_call(self, target, args, kwargs, caller_info):
        return self._pop_matching(FunctionCall(target, args, kwargs, caller_info), UnexpectedCall)

    def pop_matching_setattr(self, target, name, value, caller_info):
        return self._pop_matching(Setattr(target, name, value, caller_info), UnexpectedSetattr)

    def _push(self, queued_object):
        return self._recording_group.push(queued_object)

    def _pop_matching(self, queued_object, unexpected_class):
        popped = self._root_group.pop_matching(queued_object)
        if popped is None:
            self._log_exception_context()
            raise unexpected_class(self.get_available(), queued_object)
        return popped

    def _log_exception_context(self):
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_value is not None:
            _logger.debug("In exception context:\n%s\n%s: %s",
                          "".join(traceback.format_tb(exc_tb)), exc_type.__name__, exc_value)

    @contextmanager
    def _get_group_context(self, group_class):
        group = group_class()
        try:
            self._recording_group.push(group)
            self._recording_group = group
            yield
        finally:
            parent = group.get_parent()
            if group.is_empty():
                parent.discard_child(group)
            self._recording_group = parent

    def get_any_order_group_context(self):
        return self._get_group_context(AnyOrderGroup)

    def get_ordered_group_context(self):
        return self._get_group_context(OrderedGroup)

    def get_interleaved_group_context(self):
        return self._get_group_context(InterleavedGroup)

    def verify(self):
        expected_events = self._root_group.get_expected()
        if expected_events:
            raise ExpectedEventsNotFound(expected_events)

    def __repr__(self):
        return "ForgeQueue(_root_group <id %s>=%s, _recording_group=<id %s>)" % (id(self._root_group),
            repr(self._root_group), id(self._recording_group))
