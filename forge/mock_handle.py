from dtypes import NOTHING
from exceptions import UnauthorizedMemberAccess

class MockHandle(object):
    def __init__(self, forge, mock, mocked_class):
        super(MockHandle, self).__init__()
        self.forge = forge
        self.mock = mock
        self.mocked_class = mocked_class
        self._initialized_stubs = {}
        self._is_hashable = False
    def is_hashable(self):
        return self._is_hashable
    def enable_hashing(self):
        self._is_hashable = True
    def disable_hashing(self):
        self._is_hashable = False
    def has_attribute(self, attr):
        return False
    def get_attribute(self, attr):
        if self.has_method(attr):
            return self.get_method(attr)
        raise AttributeError("%s object has no attribute %s" % (self.mocked_class, attr))
    def has_method(self, attr):
        return attr in self._initialized_stubs or hasattr(self.mocked_class, attr)
    def get_method(self, name):
        returned = self._initialized_stubs.get(name)
        if returned is None:
            if not self.forge.is_recording():
                raise UnauthorizedMemberAccess(self.mock, name)
            real_method = getattr(self.mocked_class, name, NOTHING)
            returned = self.forge.create_method_stub(real_method)
            self._bind_if_needed(returned)
            self._initialized_stubs[name] = returned
        return returned
    def handle_special_method_call(self, name, *args, **kwargs):
        if not self.has_method(name):
            raise TypeError("%s instance has no attribute %r" % (self.mocked_class, name))
        return self.get_method(name)(*args, **kwargs)
    def _bind_if_needed(self, method_stub):
        if method_stub.__forge__.is_bound():
            return
        if method_stub.__forge__.signature.is_class_method():
            method_stub.__forge__.bind(self.mocked_class)
        elif method_stub.__forge__.signature.is_method():
            method_stub.__forge__.bind(self.mock)

