from handle import ForgeHandle

class MockHandle(ForgeHandle):
    def __init__(self, forge, mock):
        super(MockHandle, self).__init__(forge)
        self.mock = mock
        self._attributes = {}
        self._is_hashable = False
    def is_hashable(self):
        return self._is_hashable
    def enable_hashing(self):
        self._is_hashable = True
    def disable_hashing(self):
        self._is_hashable = False
    def has_attribute(self, attr):
        return False
    def get_attribute(self, attr):
        if attr in self._attributes:
            return self._attributes[attr]
        if self.has_nonmethod_class_member(attr):
            return self.get_nonmethod_class_member(attr)
        if self.has_method(attr):
            return self.get_method(attr)
        raise AttributeError("%s has no attribute %s" % (self, attr))
    def set_attribute(self, attr, value):
        if not self.forge.is_recording():
            raise AttributeError("Cannot set attribute %r" % (attr,))
        self._attributes[attr] = value
    def has_method(self, attr):
        return self.forge.methods.has_initialized_method_stub(self.mock, attr) or self._has_method(attr)
    def _has_method(self, name):
        raise NotImplementedError()
    def has_nonmethod_class_member(self, name):
        raise NotImplementedError()
    def get_nonmethod_class_member(self, name):
        raise NotImplementedError()
    def get_method(self, name):
        returned = self.forge.methods.get_initialized_method_stub_or_none(self.mock, name)
        if returned is None:
            real_method = self._get_real_method(name)
            if not self.forge.is_recording():
                self._check_unrecorded_method_getting(name)
            returned = self.forge.create_method_stub(real_method)
            self._bind_if_needed(returned)
            self.forge.methods.add_initialized_method_stub(self.mock, name, returned)
        return returned
    def _check_unrecorded_method_getting(self, name):
        raise NotImplementedError()
    def _get_real_method(self, name):
        raise NotImplementedError()
    def handle_special_method_call(self, name, args, kwargs):
        self._check_special_method_call(name, args, kwargs)
        return self.get_method(name)(*args, **kwargs)
    def _check_special_method_call(self, name, args, kwargs):
        raise NotImplementedError()
    def is_callable(self):
        raise NotImplementedError()
    def _bind_if_needed(self, method_stub):
        if method_stub.__forge__.is_bound():
            return
        if method_stub.__forge__.signature.is_class_method():
            method_stub.__forge__.bind(self.mocked_class)
        elif method_stub.__forge__.signature.is_method():
            method_stub.__forge__.bind(self.mock)

