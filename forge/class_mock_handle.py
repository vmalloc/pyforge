import types
import functools
from sentinels import NOTHING
from types import FunctionType
from types import MethodType
from types import BuiltinMethodType
from .dtypes import MethodDescriptorType
from .exceptions import InvalidEntryPoint
from .exceptions import CannotMockFunctions
from .signature import FunctionSignature
from .mock_handle import MockHandle
from .python3_compat import build_unbound_instance_method, IS_PY3

class ClassMockHandle(MockHandle):
    def __init__(self, forge, mock, mocked_class, behave_as_instance, hybrid):
        super(ClassMockHandle, self).__init__(forge, mock, behave_as_instance)
        self._assert_is_not_function(mocked_class)
        self.mocked_class = mocked_class
        self._hybrid = hybrid
    def _describe(self):
        desc = self._get_class_description()
        type_str = 'Mock' if self.behaves_as_instance else 'Class mock'
        return "<%s of %r>" % (type_str, desc)
    def _get_class_description(self):
        return getattr(self.mocked_class, '__name__', '?')
    def _assert_is_not_function(self, mocked_class):
        if type(mocked_class) in (types.FunctionType, types.MethodType, types.BuiltinFunctionType):
            raise CannotMockFunctions("Cannot mock functions as classes. Use create_function_stub instead.")
    def _has_method(self, name):
        return hasattr(self.mocked_class, name)
    def _get_real_function(self, name):
        returned = self._get_real_method(name)
        if IS_PY3:
            if hasattr(returned, '__func__'):
                return returned.__func__
            return returned
        return returned.__func__
    def _get_real_method(self, name):
        if name == '__call__' and not self.behaves_as_instance:
            return self._get_constructor_method()
        return getattr(self.mocked_class, name, NOTHING)
    def _get_constructor_method(self):
        returned = getattr(self.mocked_class, "__init__", object.__init__)
        if type(returned) is type(object.__init__) and returned.__objclass__ is object:
            # in some cases where the class doesn't have a constructor,
            # simulate an empty ctor...
            fake_constructor = lambda self: None
            fake_constructor.__name__ = "__init__"
            returned = build_unbound_instance_method(fake_constructor, self.mocked_class)
        return returned
    def _check_unrecorded_method_getting(self, name):
        pass # unrecorded methods can be obtained, but not called...
    def _check_getting_method_stub_without_recorded_calls(self, name, stub):
        pass # also ok
    def has_nonmethod_class_member(self, name):
        value = getattr(self.mocked_class, name, NOTHING)
        if value is NOTHING:
            return False
        return type(value) not in (FunctionType, MethodType, BuiltinMethodType, MethodDescriptorType)
    def get_nonmethod_class_member(self, name):
        return getattr(self.mocked_class, name)
    def get_method(self, name):
        if self._hybrid:
            if self.forge.is_replaying() and not self.forge.stubs.has_initialized_method_stub(self.mock, name):
                return self._build_hybrid_method(name)
        return super(ClassMockHandle, self).get_method(name)
    def _build_hybrid_method(self, name):
        real_method = self._get_real_method(name)
        if not self._can_use_as_entry_point(name, real_method):
            raise InvalidEntryPoint("%s is not a method that can be used as a hybrid entry pont" % (name,))
        return functools.partial(self._get_real_function(name), self._build_hybrid_self_arg(real_method))
    def _build_hybrid_self_arg(self, method):
        sig = FunctionSignature(method)
        if sig.is_class_method() and self.behaves_as_instance:
            return self.mocked_class
        return self.mock
    def _can_use_as_entry_point(self, name, method):
        if self._is_static_method(name):
            return False
        sig = FunctionSignature(method)
        if (sig.is_bound_method() and not sig.is_class_method()) and not self.behaves_as_instance:
            return False
        return True
    def _check_special_method_call(self, name, args, kwargs):
        if name == '__call__':
            if self.behaves_as_instance and not self.is_callable():
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
        if getattr(call_method, "__self__", None) is not None:
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
            if self._is_static_method(name):
                return False, None
            if self.behaves_as_instance and not method_stub.__forge__.signature.is_bound_method():
                return True, self.mock
        return False, None
    def _is_static_method(self, method_name):
        return isinstance(self.mocked_class.__dict__.get(method_name, None), staticmethod)


