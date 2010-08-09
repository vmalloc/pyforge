from ut_utils import ForgeTestCase
from forge.stub import FunctionStub
import time
import os

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
        



