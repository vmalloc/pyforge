import types
from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
import time
orig_time_sleep = time.sleep
import os
orig_os_path_join = os.path.join

class NewStyleClass(object):
    def method(self, a, b, c):
        raise NotImplementedError()

orig_newstyle_method = NewStyleClass.method

class OldStyleClass:
    def method(self, a, b, c):
        raise NotImplementedError()
orig_oldstyle_method = OldStyleClass.method

class StubbingObjectsTest(ForgeTestCase):
    def _test__stubbing_object(self, obj, method_name, expected):
        returned = self.forge.replace_with_stub(obj, method_name)
        self.assertIsInstance(obj.method, FunctionStub)
        self.assertIs(returned, obj.method)
        self.assertIs(obj.method.__forge__.original.im_func, expected.im_func)
        self.assertIs(obj.method.__forge__.signature.func.im_func, expected.im_func)
        self.assertTrue(obj.method.__forge__.signature.is_bound())
        self.forge.restore_all_stubs()
        self.assertIs(obj.method.im_func, expected.im_func)
    def test__stubbing_new_style_objects(self):
        self._test__stubbing_object(NewStyleClass(), 'method', orig_newstyle_method)
    def test__stubbing_old_style_objects(self):
        self._test__stubbing_object(OldStyleClass(), 'method', orig_oldstyle_method)

class StubbedNewStyleClass(object):
    @classmethod
    def class_method(cls, a, b, c):
        raise NotImplementedError()
    @staticmethod
    def static_method(a, b, c):
        raise NotImplementedError()
assert 'class_method' in dir(StubbedNewStyleClass)
class StubbedOldStyleClass:
    @classmethod
    def class_method(cls, a, b, c):
        raise NotImplementedError()
    @staticmethod
    def static_method(a, b, c):
        raise NotImplementedError()


class StubbingClassMethodTest(ForgeTestCase):
    def test__stubbing_class_methods(self):
        for cls in (StubbedNewStyleClass, StubbedOldStyleClass):
            self._test__stubbing_class_methods(cls, 'class_method', False)
    def test__stubbing_static_methods(self):
        for cls in (StubbedNewStyleClass, StubbedOldStyleClass):
            self._test__stubbing_class_methods(cls, 'static_method', True)
    def _test__stubbing_class_methods(self, cls, name, is_static):
        orig = getattr(cls, name)
        self.forge.replace_with_stub(cls, name)
        func = getattr(cls, name)
        self.assertIsInstance(func, FunctionStub)
        func(1, 2, 3)
        self.forge.replay()
        func = getattr(cls, name)
        func(1, 2, 3)
        self.forge.verify()
        self.forge.reset()
        self.forge.restore_all_stubs()
        func = getattr(cls, name)
        if is_static:
            self.assertIsInstance(func, types.FunctionType)
            self.assertIsInstance(cls.__dict__[name], staticmethod)
            self.assertIs(func, orig)
        else:
            self.assertIsInstance(cls.class_method, types.MethodType)
            self.assertIsInstance(cls.__dict__[name], classmethod)
            #classmethods are re-computed on every fetch
            self.assertIsNot(func, orig)
            self.assertIs(cls.class_method.im_self, cls)
            self.assertIs(cls.class_method.im_func, orig.im_func)



class StubbingModulesTest(ForgeTestCase):
    def test__stub_c_function(self):
        self.forge.replace_with_stub(time, "sleep")
        self.assertIsInstance(time.sleep, FunctionStub)
        expected_result = 666
        time.sleep(10).and_return(expected_result)
        self.forge.replay()
        self.assertEquals(time.sleep(10), expected_result)
        self.forge.restore_all_stubs()
        self.assertIs(time.sleep, orig_time_sleep)
    def test__stub_module_functions(self):
        self.forge.replace_with_stub(os.path, "join")
        self.assertIsInstance(os.path.join, FunctionStub)
        self.assertFalse(os.path.join.__forge__.signature.has_variable_kwargs())
        self.assertTrue(os.path.join.__forge__.signature.has_variable_args())
        return_path = "return_path"
        os.path.join("a", "b", "c").and_return(return_path)
        self.forge.replay()
        self.assertEquals(return_path, os.path.join("a", "b", "c"))
        self.forge.verify()
        self.forge.restore_all_stubs()
        self.assertIs(os.path.join, orig_os_path_join)
