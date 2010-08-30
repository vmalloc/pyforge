from mock_handle import MockHandle
from exceptions import MockObjectUnhashable
from exceptions import UnexpectedCall

class MockObject(object):
    def __getattr__(self, attr):
        return self.__forge__.get_attribute(attr)
    def __setattr__(self, attr, value):
        if attr == '__forge__':
            self.__dict__[attr] = value
        else:
            self.__forge__.set_attribute(attr, value)
    def __hash__(self):
        if not self.__forge__.is_hashable():
            raise MockObjectUnhashable("%s is not hashable!" % (self,))
        return id(self)
    def __nonzero__(self):
        try:
            return self.__forge__.handle_special_method_call('__nonzero__', (), {})
        except TypeError:
            return True
    def __exit__(self, *args):
        if self.__forge__.forge.is_replaying() and isinstance(args[1], UnexpectedCall):
            return
        return self.__forge__.handle_special_method_call('__exit__', args, {})
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
    '__call__',
    '__contains__',
    '__enter__',
    ]:
    setattr(MockObject, special_method_name,
            _get_special_method_placeholder(special_method_name))
