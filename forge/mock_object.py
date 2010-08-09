from mock_handle import MockHandle
from exceptions import MockObjectUnhashable

class MockObject(object):
    def __init__(self, forge, mocked_class):
        super(MockObject, self).__init__()
        self.__forge__ = MockHandle(forge, self, mocked_class)
    @property
    def __class__(self):
        return self.__forge__.mocked_class
    def __getattr__(self, attr):
        if self.__forge__.has_attribute(attr):
            return self.__forge__.get_attribute(attr)
        if self.__forge__.has_method(attr):
            return self.__forge__.get_method(attr)
        raise AttributeError("%s object has no attribute %s" % (self.__forge__.mocked_class, attr))
    def __hash__(self):
        if not self.__forge__.is_hashable():
            raise MockObjectUnhashable("%s is not hashable!" % (self,))
        return id(self)
    
