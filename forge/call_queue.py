from collections import deque

class CallQueue(object):
    def __init__(self):
        super(CallQueue, self).__init__()
        self._queue = deque()
    def __len__(self):
        return len(self._queue)
    def __iter__(self):
        return iter(self._queue)
    def push(self, obj):
        self._queue.append(obj)
    def pop(self):
        return self._queue.popleft()
    def peek(self):
        return self._queue[0]
    def reset(self):
        self._queue.clear()
