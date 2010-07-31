from collections import deque
from .expected_call import ExpectedCall
from .exceptions import UnexpectedCall

class ForgeQueue(object):
    def __init__(self, forge):
        super(ForgeQueue, self).__init__()
        self._queue = deque()
        self._forge = forge
    def __len__(self):
        return len(self._queue)
    def expect_call(self, target, args, kwargs):
        self._queue.append(ExpectedCall(target, args, kwargs))
    def pop_call(self, target, args, kwargs):
        popped = self._queue[0]
        if popped.matches_call(target, args, kwargs):
            self._queue.popleft()
        else:
            raise UnexpectedCall()
