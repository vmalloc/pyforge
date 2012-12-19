from numbers import Number
from sentinels import NOTHING
from .exceptions import ConflictingActions
from .queued_object import QueuedObject


class FunctionCall(QueuedObject):
    def __init__(self, target, args, kwargs, caller_info):
        super(FunctionCall, self).__init__(caller_info)
        self.target = target
        self.args = target.__forge__.signature.get_normalized_args(args, kwargs)
        self._call_funcs = []
        self._call_funcs_with_args = []
        self._return_value = NOTHING
        self._raised_exception = NOTHING

    def matches(self, call):
        if not isinstance(call, FunctionCall):
            return False
        return self.target is call.target and self.args == call.args

    def describe(self):
        return "%s(%s)" % (
            self.target.__forge__.describe(),
            self._get_argument_string(),
            )

    def _get_argument_string(self):
        positional_args = sorted(k for k in self.args if isinstance(k, Number))
        keyword_args = sorted(k for k in self.args if not isinstance(k, Number))
        args = [repr(self.args[arg_index]) for arg_index in positional_args]
        args.extend("%s=%r" % (arg_name, self.args[arg_name])
                    for arg_name in keyword_args)
        return ", ".join(args)

    def whenever(self):
        self.target.__forge__.forge.queue.allow_whenever(self)
        return self

    def and_call(self, func, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        self._call_funcs.append((func, list(args), kwargs))
        return self
    then_call = and_call

    def and_call_with_args(self, func):
        self._call_funcs_with_args.append(func)
        return self
    then_call_with_args = and_call_with_args

    def and_raise(self, exc):
        if self._return_value is not NOTHING:
            raise ConflictingActions()
        self._raised_exception = exc
        return exc
    then_raise = and_raise

    def and_return(self, rv):
        if self._raised_exception is not NOTHING:
            raise ConflictingActions()
        self._return_value = rv
        return rv
    then_return = and_return

    def do_side_effects(self, args, kwargs):
        for call_func, args, kwargs in self._call_funcs:
            call_func(*args, **kwargs)
        for call_func in self._call_funcs_with_args:
            call_func(*args, **kwargs)
        if self._raised_exception is not NOTHING:
            raise self._raised_exception

    def get_return_value(self):
        if self._return_value is not NOTHING:
            return self._return_value
        return None
