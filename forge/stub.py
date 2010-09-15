from .stub_handle import StubHandle
from .dtypes import WILDCARD_FUNCTION

class FunctionStub(object):
    def __init__(self, forge, original, name=None):
        super(FunctionStub, self).__init__()
        self.__forge__ = StubHandle(forge, self, original, name)
        self.__name__ = original.__name__ if name is None else name
        self.__doc__ = original.__doc__
    def __call__(*args, **kwargs):
        # we use args[0] instead of 'self' to enable functions with a 'self' argument
        return args[0].__forge__.handle_call(args[1:], kwargs)
    def __repr__(self):
        return '<Stub for %r>' % self.__forge__.get_name()

