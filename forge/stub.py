from signature import FunctionSignature
from exceptions import SignatureException

class FunctionStub(object):
    def __init__(self, forge, original, obj=None):
        super(FunctionStub, self).__init__()
        self._forge = forge
        self._original = original
        self._obj = obj
        self._signature = FunctionSignature(self._original)
        self.__name__ = original.__name__
        self.__doc__ = original.__doc__
    def __call__(self, *args, **kwargs):
        if self._obj is not None and not self._signature.can_be_called_as_method():
            raise SignatureException("%s cannot be called as method!" % (self,))
        if self._forge.is_recording():
            return self._handle_recorded_call(args, kwargs)
        else:
            return self._handle_replay_call(args, kwargs)
    def _handle_recorded_call(self, args, kwargs):
        return self._forge.queue.expect_call(self, args, kwargs)
    def _handle_replay_call(self, args, kwargs):
        expected_call = self._forge.queue.pop_call(self, args, kwargs)
        return_value = expected_call.get_return_value()
        #might raise...
        expected_call.do_side_effects(args, kwargs)
        return return_value
