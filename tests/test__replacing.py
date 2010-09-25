import types
from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
from forge.class_mock import ClassMockObject
import time
orig_time_sleep = time.sleep
import os
orig_os_path_join = os.path.join

class NewStyleClass(object):
    def method(self, a, b, c):
        raise NotImplementedError()
    @property
    def some_property(self):
        return 2

orig_newstyle_method = NewStyleClass.method
orig_newstyle_property = NewStyleClass.some_property

class OldStyleClass:
    def method(self, a, b, c):
        raise NotImplementedError()
    @property
    def some_property(self):
        return 2

orig_oldstyle_method = OldStyleClass.method
orig_oldstyle_property = OldStyleClass.some_property

class StubbingObjectsTest(ForgeTestCase):
    def _test__stubbing_object(self, obj):
        expected = obj.method
        returned = self.forge.replace(obj, 'method')
        self.assertIsInstance(obj.method, FunctionStub)
        self.assertIs(returned, obj.method)
        self.assertIs(obj.method.__forge__.original.im_func, expected.im_func)
        self.assertIs(obj.method.__forge__.signature.func.im_func, expected.im_func)
        self.assertTrue(obj.method.__forge__.is_bound())
        self.forge.restore_all_replacements()
        self.assertIs(obj.method.im_func, expected.im_func)
    def test__stubbing_new_style_objects(self):
        self._test__stubbing_object(NewStyleClass())
    def test__stubbing_old_style_objects(self):
        self._test__stubbing_object(OldStyleClass())

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
        self.forge.replace(cls, name)
        func = getattr(cls, name)
        self.assertIsInstance(func, FunctionStub)
        func(1, 2, 3)
        self.forge.replay()
        func = getattr(cls, name)
        func(1, 2, 3)
        self.forge.verify()
        self.forge.reset()
        self.forge.restore_all_replacements()
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
        self.forge.replace(time, "sleep")
        self.assertIsInstance(time.sleep, FunctionStub)
        expected_result = 666
        time.sleep(10).and_return(expected_result)
        self.forge.replay()
        self.assertEquals(time.sleep(10), expected_result)
        self.forge.restore_all_replacements()
        self.assertIs(time.sleep, orig_time_sleep)
    def test__stub_module_functions(self):
        self.forge.replace(os.path, "join")
        self.assertIsInstance(os.path.join, FunctionStub)
        self.assertFalse(os.path.join.__forge__.signature.has_variable_kwargs())
        self.assertTrue(os.path.join.__forge__.signature.has_variable_args())
        return_path = "return_path"
        os.path.join("a", "b", "c").and_return(return_path)
        self.forge.replay()
        self.assertEquals(return_path, os.path.join("a", "b", "c"))
        self.forge.verify()
        self.forge.restore_all_replacements()
        self.assertIs(os.path.join, orig_os_path_join)

class ReplacingTest(ForgeTestCase):
    def test__replacing_simple_attributes(self):
        s = self.forge.create_sentinel()
        s.a = 2
        self.forge.replace_with(s, "a", 3)
        self.assertEquals(s.a, 3)
        self.forge.restore_all_replacements()
        self.assertEquals(s.a, 2)
    def test__replacing_properties__new_style(self):
        self._test__replacing_properties(NewStyleClass, orig_newstyle_property)
    def test__replacing_properties__old_style(self):
        self._test__replacing_properties(OldStyleClass, orig_oldstyle_property)
    def _test__replacing_properties(self, cls, orig):
        self.forge.replace_with(cls, "some_property", 3)
        self.assertEquals(cls.some_property, 3)
        self.assertEquals(cls().some_property, 3)
        self.forge.restore_all_replacements()
        self.assertIs(cls.some_property, orig)
        self.assertIs(cls().some_property, 2)

class NonFunctionStubbingTest(ForgeTestCase):
    def setUp(self):
        super(NonFunctionStubbingTest, self).setUp()
        self.x = self.forge.create_sentinel()
    def test__replacing_new_style_class_objects(self):
        class MyClass(object):
            pass
        self._test__replacing_objects(MyClass(), MyClass)
    def test__replacing_old_style_class_objects(self):
        class MyClass:
            pass
        self._test__replacing_objects(MyClass(), MyClass)
    def test__replacing_builtin_objects(self):
        from cStringIO import StringIO
        self._test__replacing_objects(StringIO(), type(StringIO()))
    def _test__replacing_objects(self, obj, cls):
        orig = self.x.obj = obj
        self.forge.replace(self.x, 'obj')
        self.assertIsInstance(self.x.obj, ClassMockObject)
        self.assertTrue(self.x.obj.__forge__.behaves_as_instance)
        self.assertIs(self.x.obj.__forge__.mocked_class, cls)
        self.forge.restore_all_replacements()
        self.assertIs(self.x.obj, orig)
    def test__replacing_new_style_classes(self):
        class MyClass(object):
            pass
        self._test__replacing_classes(MyClass)
    def test__stubbing_old_new_style_classes(self):
        class MyClass:
            pass
        self._test__replacing_classes(MyClass)
    def _test__replacing_classes(self, cls):
        self.x.cls = cls
        self.forge.replace(self.x, 'cls')
        self.assertIsInstance(self.x.cls, ClassMockObject)
        self.assertIs(self.x.cls.__forge__.mocked_class, cls)
        self.assertFalse(self.x.cls.__forge__.behaves_as_instance)
        self.forge.restore_all_replacements()
        self.assertIs(self.x.cls, cls)

class MultipleStubbingTest(ForgeTestCase):
    def test__multiple_stubbing(self):
        self.forge.replace(self.forge, "replace")

        some_object = self.forge.create_sentinel()

        expected_results = [
            self.forge.replace(some_object, x).and_return(object())
            for x in ["a", "b", "c"]
            ]

        self.forge.replay()

        returned = self.forge.replace_many(some_object, "a", "b", "c")
        self.assertEquals(returned, expected_results)
        self.forge.restore_all_replacements()
        self.forge.verify()
        self.assertNoMoreCalls()
        self.forge.reset()
