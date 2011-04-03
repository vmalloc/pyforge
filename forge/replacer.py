from contextlib import contextmanager
from types import ModuleType
from .utils import is_class
from .utils import is_function
from .utils import is_bound_method

class Replacer(object):
    def __init__(self, forge):
        super(Replacer, self).__init__()
        self.forge = forge
        self._stubs = []
    def replace(self, obj, attr_name):
        return self._replace(obj, attr_name).stub
    def _replace(self, obj, attr_name):
        replaced = getattr(obj, attr_name)
        replacement = self._get_replacement(replaced)
        self._set_replacement_description(replacement, obj, attr_name)
        return self._replace_with(obj, attr_name, replacement)
    @contextmanager
    def replacing_context(self, obj, attr_name):
        installed = self._replace(obj, attr_name)
        try:
            yield None
        finally:
            installed.restore()
    def _get_replacement(self, replaced):
        if is_class(replaced):
            return self.forge.create_class_mock(replaced)
        if is_function(replaced):
            return self.forge.create_function_stub(replaced)
        if is_bound_method(replaced):
            return self.forge.create_method_stub(replaced)
        return self.forge.create_mock(self._get_class(replaced))
    def _get_class(self, obj):
        return getattr(obj, "__class__", type(obj))
    def _set_replacement_description(self, replacement, obj, attr_name):
        if isinstance(obj, ModuleType):
            obj_name = obj.__name__
        else:
            obj_name = "<%s instance>" % (type(obj).__name__,)
        replacement.__forge__.set_description("%s.%s" % (obj_name, attr_name))
    def _replace_object_method_with_stub(self, obj, method_name):
        return self.replace_with(obj, method_name,
                                 self.forge.create_method_stub(getattr(obj, method_name)))
    def _replace_module_function_with_stub(self, module, function_name):
        return self.replace_with(module, function_name,
                                       self.forge.create_function_stub(getattr(module, function_name)))
    def replace_with(self, obj, attr_name, stub):
        self._replace_with(obj, attr_name, stub)
        return stub
    def _replace_with(self, obj, attr_name, stub):
        installed = InstalledStub(obj, attr_name, stub)
        self._stubs.append(installed)
        setattr(obj, attr_name, stub)
        return installed
    def restore_all(self):
        while self._stubs:
            installed = self._stubs.pop(-1)
            installed.restore()

class InstalledStub(object):
    def __init__(self, obj, method_name, stub):
        super(InstalledStub, self).__init__()
        self.obj = obj
        self.method_name = method_name
        self.restorer = self._get_restorer(obj, method_name)
        self.stub = stub
    def restore(self):
        self.restorer.restore()
    def _get_restorer(self, obj, method_name):
        orig = obj.__dict__.get(method_name)
        if orig is None:
            orig = getattr(obj, method_name)
        return SimpleRestorer(obj, method_name, orig)

class Restorer(object):
    def __init__(self, obj, method_name, orig):
        super(Restorer, self).__init__()
        self.obj, self.method_name = obj, method_name
        self.orig = orig
    def restore(self):
        raise NotImplementedError()

class SimpleRestorer(Restorer):
    def restore(self):
        setattr(self.obj, self.method_name, self.orig)
