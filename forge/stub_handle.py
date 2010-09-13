from handle import ForgeHandle
from signature import FunctionSignature
from exceptions import SignatureException

class StubHandle(ForgeHandle):
    def __init__(self, forge, stub, original):
        super(StubHandle, self).__init__(forge)
        self.stub = stub
        self.original = original
        self.signature = FunctionSignature(self.original)
        self._obj = None
    def bind(self, obj):
        if not self.signature.is_method():
            raise SignatureException("%s cannot be bound!" % self.stub)
        if self.signature.is_bound() or self._obj is not None:
            raise SignatureException("%s is already bound!" % self.stub)
        self._obj = obj
    def handle_call(self, args, kwargs):
        if self.forge.is_recording():
            returned = self._handle_recorded_call(args, kwargs)
            self.forge.stubs.mark_stub_recorded(self.stub)
            return returned
        else:
            return self._handle_replay_call(args, kwargs)
    def _handle_recorded_call(self, args, kwargs):
        args, kwargs = self._update_bound_args_kwargs(args, kwargs)
        return self.forge.queue.push_call(self.stub, args, kwargs)
    def _handle_replay_call(self, args, kwargs):
        args, kwargs = self._update_bound_args_kwargs(args, kwargs)
        expected_call = self.forge.queue.pop_matching_call(self.stub, args, kwargs)
        return_value = expected_call.get_return_value()
        #might raise...
        expected_call.do_side_effects(args, kwargs)
        return return_value
    def _update_bound_args_kwargs(self, args, kwargs):
        if self._obj is not None:
            args = [self._obj] + list(args)
        return args, kwargs
    def is_bound(self):
        return self._obj is not None or self.signature.is_bound()
    def has_recorded_calls(self):
        return self.forge.stubs.was_stub_recorded(self.stub)

