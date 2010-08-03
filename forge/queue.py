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
        self._queue.append(FunctionCall(target, args, kwargs))
    def pop_call(self, target, args, kwargs):
        popped = self._queue[0]
        if popped.matches_call(target, args, kwargs):
            self._queue.popleft()
        else:
            raise UnexpectedCall(popped, FunctionCall(target, args, kwargs), target._signature.is_method())
    def verify(self):
        if self._queue:
            raise ExpectedCallsNotFound(self._queue)
