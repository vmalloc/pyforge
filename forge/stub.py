import functools
from .stub_handle import StubHandle
from .dtypes import WILDCARD_FUNCTION

class FunctionStub(object):
    def __init__(self, forge, original, name=None):
        super(FunctionStub, self).__init__()
        self.__forge__ = StubHandle(forge, self, original, name=name)
        self.__name__ = original.__name__ if name is None else name
        self.__doc__ = original.__doc__
    def __call__(*args, **kwargs):
        self = args[0]
        caller_info = self.__forge__.forge.debug.get_caller_info()
        return self.__forge__.handle_call(args[1:], kwargs, caller_info=caller_info)
    def __repr__(self):
        call_count_msg = ""
        if self.__forge__.call_count:
            call_count_msg += " (already called %s times)" % (self.__forge__.call_count,)
        return '<Stub for %r%s>' % (self.__forge__.describe(), call_count_msg)
    def __getattribute__(self, name):
        if name == "when" and self.__forge__.forge.is_recording():
            return functools.partial(_when, self)
        return super(FunctionStub, self).__getattribute__(name)

def _when(__func, *args, **kwargs):
    return __func(*args, **kwargs).whenever()
