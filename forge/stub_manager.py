class StubManager(object):
    def __init__(self, forge):
        super(StubManager, self).__init__()
        self.forge = forge
        self._stubs = []
    def replace_with_stub(self, obj, method_name):
        returned = self.forge.create_method_stub(getattr(obj, method_name), obj)
        setattr(obj, method_name, returned)
        self._stubs.append(InstalledStub(obj, method_name, getattr(obj, method_name)))
        return returned
    def restore_all_stubs(self):
        while self._stubs:
            installed = self._stubs.pop(-1)
            installed.restore()            

class InstalledStub(object):
    def __init__(self, obj, method_name, orig):
        super(InstalledStub, self).__init__()
        self.obj = obj
        self.method_name = method_name
        self.orig = orig
    def restore(self):
        delattr(self.obj, self.method_name)
