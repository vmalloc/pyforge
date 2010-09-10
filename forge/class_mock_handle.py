from mock_handle import MockHandle
from .dtypes import NOTHING
from types import FunctionType
from types import MethodType

class ClassMockHandle(MockHandle):
    def __init__(self, forge, mock, mocked_class, behave_as_instance):
        super(ClassMockHandle, self).__init__(forge, mock, behave_as_instance)
        self.mocked_class = mocked_class
    def _has_method(self, name):
        return hasattr(self.mocked_class, name)
    def _get_real_method(self, name):
        if name == '__call__' and not self.behaves_as_instance:
            return self.mocked_class.__init__
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
    def _is_binding_needed(self, name, method_stub):
        if not method_stub.__forge__.is_bound():
            if name == '__call__' and not self.behaves_as_instance:
                # constructors are normally bound...
                return True, NOTHING
            if method_stub.__forge__.signature.is_class_method():
                return True, self.mocked_class
            if self.behaves_as_instance and method_stub.__forge__.signature.is_method():
                return True, self.mock
        return False, None


