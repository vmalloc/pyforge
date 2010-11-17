from .mock_object import MockObject
from .wildcard_mock_handle import WildcardMockHandle

class WildcardMockObject(MockObject):
    def __init__(self, forge, name=None):
        super(WildcardMockObject, self).__init__()
        self.__forge__ = WildcardMockHandle(forge, self, name=name)
    def __repr__(self):
        return self.__forge__.describe()
