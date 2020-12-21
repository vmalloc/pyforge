from .ut_utils import ForgeTestCase
from forge import InvalidEntryPoint

class TestedClass(object):
    def entry_point(self):
        self.f()
        self.g(1, 2, 3)
        self.h(a=1, b=2)
        self.class_method()
        self.static_method()
    def set_value(self):
        self.value = 2
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
    def class_method_entry_point(cls):
        return cls
    @staticmethod
    def static_method_entry_point(arg):
        pass

class HybridMockTest(ForgeTestCase):
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(HybridMockTest, self).tearDown()
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
    def test__can_call_class_methods(self):
        hm = self.forge.create_hybrid_mock(TestedClass)
        self.forge.replay()
        rv = hm.class_method_entry_point()
        # the 'cls' argument should be the class itself
        self.assertIs(rv, TestedClass)
    def test__can_call_class_methods_on_class_mocks(self):
        hm = self.forge.create_hybrid_class_mock(TestedClass)
        self.forge.replay()
        rv = hm.class_method_entry_point()
        # for class mocks, the 'cls' argument should be the mock!
        self.assertIs(rv, hm)
    def test__cannot_call_static_methods(self):
        hm = self.forge.create_hybrid_mock(TestedClass)
        self.forge.replay()
        with self.assertRaises(InvalidEntryPoint):
            hm.static_method_entry_point()
    def test__hybrid_mocks_setting_values(self):
        hm = self.forge.create_hybrid_mock(TestedClass)
        hm.__forge__.enable_setattr_during_replay()
        self.forge.replay()
        hm.set_value()
        self.assertEqual(hm.value, 2)

class ClassWithClassmethodConstructor(object):
    def __init__(self, a, b, c):
        pass
    @classmethod
    def constructor(cls, a, b, c):
        return cls(a, b, c)

class HybridClassMockTest(ForgeTestCase):
    def setUp(self):
        super(HybridClassMockTest, self).setUp()
        self.mock = self.forge.create_hybrid_class_mock(ClassWithClassmethodConstructor)
    def test__expecting_construction(self):
        expected = self.mock(1, 2, 3).and_return(self.forge.create_mock(ClassWithClassmethodConstructor))
        self.forge.replay()
        got = self.mock.constructor(1, 2, 3)
        self.assertIs(expected, got)
