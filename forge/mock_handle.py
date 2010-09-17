from handle import ForgeHandle

class MockHandle(ForgeHandle):
    def __init__(self, forge, mock, behave_as_instance=True):
        super(MockHandle, self).__init__(forge)
        self.mock = mock
        self.behaves_as_instance = behave_as_instance
        self._attributes = {}
        self._is_hashable = False
    def describe(self):
        raise NotImplementedError()
    def is_hashable(self):
        return self._is_hashable
    def enable_hashing(self):
        self._is_hashable = True
    def disable_hashing(self):
        self._is_hashable = False
    def has_attribute(self, attr):
        return False
    def get_attribute(self, attr):
        if self.forge.attributes.has_attribute(self.mock, attr):
            return self.forge.attributes.get_attribute(self.mock, attr)
        if self.has_nonmethod_class_member(attr):
            return self.get_nonmethod_class_member(attr)
        if self.has_method(attr):
            return self.get_method(attr)
        raise AttributeError("%s has no attribute %r" % (self.mock, attr))
    def set_attribute(self, attr, value):
        if self.forge.is_recording():
            self._set_attribute(attr, value)
        else:
            self._set_attribute_during_replay(attr, value)
    def expect_setattr(self, attr, value):
        return self.forge.queue.push_setattr(self.mock, attr, value)
    def _set_attribute_during_replay(self, attr, value):
        self.forge.queue.pop_matching_setattr(self.mock, attr, value)
        self._set_attribute(attr, value)
    def _set_attribute(self, attr, value):
        self.forge.attributes.set_attribute(self.mock, attr, value)
    def has_method(self, attr):
        return self.forge.stubs.has_initialized_method_stub(self.mock, attr) or self._has_method(attr)
    def _has_method(self, name):
        raise NotImplementedError()
    def has_nonmethod_class_member(self, name):
        raise NotImplementedError()
    def get_nonmethod_class_member(self, name):
        raise NotImplementedError()
    def get_method(self, name):
        returned = self.forge.stubs.get_initialized_method_stub_or_none(self.mock, name)
        if returned is None:
            real_method = self._get_real_method(name)
            if not self.forge.is_recording():
                self._check_unrecorded_method_getting(name)
            returned = self._construct_stub(name, real_method)
            self._bind_if_needed(name, returned)
            self.forge.stubs.add_initialized_method_stub(self.mock, name, returned)
        elif self.forge.is_replaying() and not returned.__forge__.has_recorded_calls():
            self._check_getting_method_stub_without_recorded_calls(name, returned)
        return returned
    def _construct_stub(self, name, real_method):
        return self.forge.create_method_stub(real_method, parent=self.mock)
    def _check_unrecorded_method_getting(self, name):
        raise NotImplementedError()
    def _check_getting_method_stub_without_recorded_calls(self, name, stub):
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
    def _bind_if_needed(self, name, method_stub):
        bind_needed, bind_target = self._is_binding_needed(name, method_stub)
        if bind_needed:
            method_stub.__forge__.bind(bind_target)
    def _is_binding_needed(self, name, method_stub):
        raise NotImplementedError()
