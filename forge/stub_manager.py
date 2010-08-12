import types

class StubManager(object):
    def __init__(self, forge):
        super(StubManager, self).__init__()
        self.forge = forge
        self._stubs = []
    def replace_with_stub(self, obj, method_name):
        if isinstance(obj, types.ModuleType):
            return self._replace_module_function_with_stub(obj, method_name)
        return self._replace_object_method_with_stub(obj, method_name)

    def _replace_object_method_with_stub(self, obj, method_name):
        return self._replace_with_stub(obj, method_name,
                                       self.forge.create_method_stub(getattr(obj, method_name)))
    def _replace_module_function_with_stub(self, module, function_name):
        return self._replace_with_stub(module, function_name,
                                       self.forge.create_function_stub(getattr(module, function_name)))
    def _replace_with_stub(self, obj, attr_name, stub):
        orig = getattr(obj, attr_name)
        self._stubs.append(InstalledStub(obj, attr_name, stub))
        setattr(obj, attr_name, stub)
        return stub
    def restore_all_stubs(self):
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
