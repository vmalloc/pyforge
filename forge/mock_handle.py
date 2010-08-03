from dtypes import NOTHING
from exceptions import UnauthorizedMemberAccess

class MockHandle(object):
    def __init__(self, forge, mock, mocked_class):
        super(MockHandle, self).__init__()
        self.forge = forge
        self.mock = mock
        self.mocked_class = mocked_class
        self._initialized_stubs = {}
    def has_attribute(self, attr):
        return False
    def get_attribute(self, attr):
        raise NotImplementedError()
    def has_method(self, attr):
        return attr in self._initialized_stubs or hasattr(self.mocked_class, attr)
    def get_method(self, name):
        returned = self._initialized_stubs.get(name)
        if returned is None:
            if not self.forge.is_recording():
                raise UnauthorizedMemberAccess(self.mock, name)
            real_method = getattr(self.mocked_class, name, NOTHING)
            returned = self.forge.create_method_stub(real_method, self)
            self._initialized_stubs[name] = returned
        return returned

