from .stub_handle import StubHandle

class FunctionStub(object):
    def __init__(self, forge, original):
        super(FunctionStub, self).__init__()
        self.__forge__ = StubHandle(forge, self, original)
        self.__name__ = original.__name__
        self.__doc__ = original.__doc__
    def __call__(self, *args, **kwargs):
        return self.__forge__.handle_call(args, kwargs)

