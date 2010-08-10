from collections import deque
from .function_call import FunctionCall
from .exceptions import UnexpectedCall
from .exceptions import ExpectedCallsNotFound

class ForgeQueue(object):
    def __init__(self, forge):
        super(ForgeQueue, self).__init__()
        self._queue = deque()
        self._forge = forge
    def __len__(self):
        return len(self._queue)
    def expect_call(self, target, args, kwargs):
        returned = FunctionCall(target, args, kwargs)
        self._queue.append(returned)
        return returned
    def pop_call(self, target, args, kwargs):
        if self._queue:
            popped = self._queue[0]
        else:
            popped = None
        if popped is not None and popped.matches_call(target, args, kwargs):
            self._queue.popleft()
        else:
            raise UnexpectedCall(popped, FunctionCall(target, args, kwargs))
        return popped
    def verify(self):
        if self._queue:
            raise ExpectedCallsNotFound(self._queue)
