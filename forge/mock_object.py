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

def _get_special_method_placeholder(name):
    def placeholder(self, *args, **kwargs):
        return self.__forge__.handle_special_method_call(name, args, kwargs)
    placeholder.__name__ = name
    return placeholder


for special_method_name in [
    '__delitem__',
    '__getitem__',
    '__len__',
    '__setitem__',
    '__iter__',
    ]:
    setattr(MockObject, special_method_name,
            _get_special_method_placeholder(special_method_name))
