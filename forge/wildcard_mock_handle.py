from .mock_handle import MockHandle
from .constants import WILDCARD_DESCRIPTION
from .dtypes import WILDCARD_FUNCTION

class WildcardMockHandle(MockHandle):
    def __init__(self, forge, mock, name=None):
        super(WildcardMockHandle, self).__init__(forge, mock)
        self.__name__ = name
    def _has_method(self, name):
        return True
    def _describe(self):
        if self.__name__:
            return "<<Wildcard %s>>" % self.__name__
        else:
            return WILDCARD_DESCRIPTION
    def _get_real_method(self, name):
        return WILDCARD_FUNCTION
    def _construct_stub(self, name, real_method):
        return self.forge.create_method_stub(real_method, name=name)
    def _check_unrecorded_method_getting(self, name):
        self._raise_attribute_error(name)
    def _check_getting_method_stub_without_recorded_calls(self, name, stub):
        self._raise_attribute_error(name)
    def _raise_attribute_error(self, name):
        raise AttributeError("%s has no attribute %s" % (self.mock, name))
    def has_nonmethod_class_member(self, name):
        return False
    def _check_special_method_call(self, *_, **__):
        pass
    def _is_binding_needed(self, name, stub):
        return False, None

