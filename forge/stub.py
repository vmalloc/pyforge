from signature import FunctionSignature

class FunctionStub(object):
    def __init__(self, forge, original):
        super(FunctionStub, self).__init__()
        self._forge = forge
        self._original = original
        self._signature = FunctionSignature(self._original)
        self.__name__ = original.__name__
        self.__doc__ = original.__doc__
    def __call__(self, *args, **kwargs):
        if self._forge.is_recording():
            self._handle_recorded_call(args, kwargs)
        else:
            self._handle_replay_call(args, kwargs)
    def _handle_recorded_call(self, args, kwargs):
        self._forge.queue.expect_call(self, args, kwargs)
    def _handle_replay_call(self, args, kwargs):
        self._forge.queue.pop_call(self, args, kwargs)
