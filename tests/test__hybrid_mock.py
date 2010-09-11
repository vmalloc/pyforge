from ut_utils import ForgeTestCase
from forge import InvalidEntryPoint

class TestedClass(object):
    def entry_point(self):
        self.f()
        self.g(1, 2, 3)
        self.h(a=1, b=2)
        self.class_method()
        self.static_method()
    def f(self):
        raise NotImplementedError()
    @classmethod
    def class_method(self):
        pass
    @staticmethod
    def static_method():
        pass
    def g(self, a, b, c):
        raise NotImplementedError()
    def h(self, a, b):
        raise NotImplementedError()
    @classmethod
    def class_method_entry_point(self):
        pass
    @staticmethod
    def static_method_entry_point(self):
        pass

class HybridMockTest(ForgeTestCase):
    def test__hybrid_mock(self):
        hm = self.forge.create_hybrid_mock(TestedClass)
        # these will be stubbed
        hm.f()
        hm.g(1, 2, 3)
        hm.h(1, 2)
        hm.class_method()
        hm.static_method()
        self.forge.replay()
        hm.entry_point()
        self.forge.verify()
    def test__cannot_call_class_methods(self):
        hm = self.forge.create_hybrid_mock(TestedClass)
        self.forge.replay()
        with self.assertRaises(InvalidEntryPoint):
            hm.class_method_entry_point()
    def test__cannot_call_static_methods(self):
        hm = self.forge.create_hybrid_mock(TestedClass)
        self.forge.replay()
        with self.assertRaises(InvalidEntryPoint):
            hm.static_method_entry_point()

