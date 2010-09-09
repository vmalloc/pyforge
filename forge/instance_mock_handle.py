from mock_handle import MockHandle
from .dtypes import NOTHING
from types import FunctionType
from types import MethodType

class InstanceMockHandle(MockHandle):
    def __init__(self, forge, mock, mocked_class):
        super(InstanceMockHandle, self).__init__(forge, mock)
        self.mocked_class = mocked_class
    def _has_method(self, name):
        return hasattr(self.mocked_class, name)
    def _get_real_method(self, name):
        return getattr(self.mocked_class, name, NOTHING)
    def _check_unrecorded_method_getting(self, name):
        pass # unrecorded methods can be obtained, but not called...
    def _check_getting_method_stub_without_recorded_calls(self, name, stub):
        pass # also ok
    def has_nonmethod_class_member(self, name):
        value = getattr(self.mocked_class, name, NOTHING)
        if value is NOTHING:
            return False
        return type(value) not in (FunctionType, MethodType)
    def get_nonmethod_class_member(self, name):
        return getattr(self.mocked_class, name)
    def _check_special_method_call(self, name, args, kwargs):
        if name == '__call__':
            if not self.is_callable():
                raise TypeError("%s instance is not callable!" % (self.mocked_class,))
        else:
            if not self.has_method(name):
                raise TypeError("%s instance has no attribute %r" % (self.mocked_class, name))
    def is_callable(self):
        if not hasattr(self.mocked_class, "__call__"):
            return False
        call_method = self.mocked_class.__call__
        if getattr(call_method, "__objclass__", None) is type(self.mocked_class):
            return False
        if getattr(call_method, "im_self", None) is not None:
            #__call__ is already bound, for some reason
            return False
        return True

