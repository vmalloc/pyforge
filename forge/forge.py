from .stub import FunctionStub
from .queue import ForgeQueue

class Forge(object):
    def __init__(self):
        super(Forge, self).__init__()
        self.reset()
    def is_replaying(self):
        return self._is_replaying
    def is_recording(self):
        return not self.is_replaying()
    def reset(self):
        self._is_replaying = False
        self.queue = ForgeQueue(self)
    def create_function_stub(self, func):
        return FunctionStub(self, func)
    def replay(self):
        self._is_replaying = True
    def verify(self):
        self.queue.verify()

