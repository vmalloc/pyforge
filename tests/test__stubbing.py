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
        self.assertIs(obj.method._original.im_func, expected.im_func)
        self.assertIs(obj.method._signature.func.im_func, expected.im_func)
        self.assertTrue(obj.method._signature.is_first_argument_self())
        self.forge.restore_all_stubs()
        self.assertIs(obj.method.im_func, expected.im_func)
    def test__stubbing_new_style_objects(self):
        self._test__stubbing_object(NewStyleClass(), 'method', orig_newstyle_method)
    def test__stubbing_old_style_objects(self):
        self._test__stubbing_object(OldStyleClass(), 'method', orig_oldstyle_method)


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
        self.assertFalse(os.path.join._signature.has_variable_kwargs())
        self.assertTrue(os.path.join._signature.has_variable_args())
        return_path = "return_path"
        os.path.join("a", "b", "c").and_return(return_path)
        self.forge.replay()
        self.assertEquals(return_path, os.path.join("a", "b", "c"))
        self.forge.verify()
        self.forge.restore_all_stubs()
        self.assertIs(os.path.join, orig_os_path_join)
