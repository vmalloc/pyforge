from .handle import ForgeHandle
from .signature import FunctionSignature
from .bound_signature_adapter import BoundSignatureAdapter

class StubHandle(ForgeHandle):
    def __init__(self, forge, stub, original, name=None):
        super(StubHandle, self).__init__(forge)
        self.stub = stub
        self.name = name
        self.original = original
        self.signature = FunctionSignature(self.original)
        self._call_count = 0
        self._call_count_session_id = 0

    @property
    def call_count(self):
        if self.forge.session_id == self._call_count_session_id:
            return self._call_count
        return 0

    def _describe(self):
        if self.name is not None:
            return self.name
        return self.original.__name__

    def bind(self, obj):
        self.signature = BoundSignatureAdapter(self.signature, obj)

    def is_bound(self):
        return self.signature.is_bound_method()

    def handle_call(self, args, kwargs, caller_info):
        if self.forge.is_recording():
            returned = self._handle_recorded_call(args, kwargs, caller_info)
            self.forge.stubs.mark_stub_recorded(self.stub)
            return returned
        else:
            return self._handle_replay_call(args, kwargs, caller_info)

    def _handle_recorded_call(self, args, kwargs, caller_info):
        return self.forge.queue.push_call(self.stub, args, kwargs, caller_info)

    def _handle_replay_call(self, args, kwargs, caller_info):
        expected_call = self.forge.queue.pop_matching_call(self.stub, args, kwargs, caller_info)
        return_value = expected_call.get_return_value()
        self._increment_call_count()
        #might raise...
        expected_call.do_side_effects(args, kwargs)
        return return_value

    def _increment_call_count(self):
        if self._call_count_session_id != self.forge.session_id:
            self._call_count_session_id = self.forge.session_id
            self._call_count = 0
        self._call_count += 1

    def has_recorded_calls(self):
        return self.forge.stubs.was_stub_recorded(self.stub)
