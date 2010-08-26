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
        return self.__forge__.get_attribute(attr)
    def __hash__(self):
        if not self.__forge__.is_hashable():
            raise MockObjectUnhashable("%s is not hashable!" % (self,))
        return id(self)
    def __len__(self):
        return self.__forge__.handle_special_method_call('__len__')
    def __setitem__(self, item, value):
        return self.__forge__.handle_special_method_call('__setitem__', item, value)

