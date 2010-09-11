from .stub_handle import StubHandle

class FunctionStub(object):
    def __init__(self, forge, original):
        super(FunctionStub, self).__init__()
        self.__forge__ = StubHandle(forge, self, original)
        self.__name__ = original.__name__
        self.__doc__ = original.__doc__
    def __call__(*args, **kwargs):
        # we use args[0] instead of 'self' to enable functions with a 'self' argument
        return args[0].__forge__.handle_call(args[1:], kwargs)
    def __repr__(self):
        return "<Stub for function %r>" % (self.__name__,)

