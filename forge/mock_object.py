from .exceptions import MockObjectUnhashable
from .exceptions import UnexpectedEvent

class MockObject(object):
    def __repr__(self):
        return self.__forge__.describe()
    def __getattr__(self, attr):
        return self.__forge__.get_attribute(attr)
    def __setattr__(self, attr, value):
        if attr == '__forge__':
            self.__dict__[attr] = value
        else:
            self.__forge__.set_attribute(attr, value, caller_info=self.__forge__.forge.debug.get_caller_info())
    def __hash__(self):
        if not self.__forge__.is_hashable():
            raise MockObjectUnhashable("%s is not hashable!" % (self,))
        return id(self)
    def __nonzero__(self):
        try:
            return self.__forge__.handle_special_method_call('__nonzero__', (), {},
                                                             caller_info=self.__forge__.forge.debug.get_caller_info())
        except TypeError:
            return True
    def __bool__(self):
        return self.__nonzero__()
    def __exit__(self, *args):
        if self.__forge__.forge.is_replaying() and isinstance(args[1], UnexpectedEvent):
            return
        return self.__forge__.handle_special_method_call('__exit__', args, {},
                                                         caller_info=self.__forge__.forge.debug.get_caller_info())
def _get_special_method_placeholder(name):
    def placeholder(self, *args, **kwargs):
        caller_info = self.__forge__.forge.debug.get_caller_info()
        return self.__forge__.handle_special_method_call(name, args, kwargs, caller_info=caller_info)
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
