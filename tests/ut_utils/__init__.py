from functools import wraps
import sys
import types
import platform
from forge import Forge
from forge.python3_compat import IS_PY3

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestCase(unittest.TestCase):
    pass

if IS_PY3:
    from io import BytesIO as BinaryObjectClass
    assert not hasattr(sys.modules[BinaryObjectClass.__module__], "__file__")
else:
    from cStringIO import StringIO as BinaryObjectClass

class ForgeTestCase(TestCase):
    def setUp(self):
        super(ForgeTestCase, self).setUp()
        self.forge = Forge()
    def tearDown(self):
        self.assertNoMoreCalls()
        self.forge.verify()
        self.forge.restore_all_replacements()
        self.forge.reset()
        super(ForgeTestCase, self).tearDown()
    def assertNoMoreCalls(self):
        expected = self.forge.queue.get_expected()
        self.assertEquals(len(expected), 0, "len=%d != 0, expected_events=%s, queue=%s" % (len(expected),
            repr(expected), repr(self.forge.queue)))

class Method(object):
    def __init__(self, signature_string):
        self.signature_string = signature_string
        self.function = self._to_function()
        self.name = self.function.__name__
    def get_function(self):
        return self.function
    def _to_function(self):
        code = """def %s: raise NotImplementedError()""" % self.signature_string
        d = {}
        exec(code, {}, d)
        if len(d) != 1:
            raise RuntimeError("More than one function created")
        [returned] = d.values()
        return returned
class ClassMethod(Method):
    def get_function(self):
        return classmethod(super(ClassMethod, self).get_function())
class StaticMethod(Method):
    def get_function(self):
        return staticmethod(super(StaticMethod, self).get_function())

def build_new_style_class(methods=()):
    return type('NewStyleClass', (object,), _get_class_dict(methods))
def build_old_style_class(methods=()):
    if IS_PY3:
        return build_new_style_class(methods)
    return types.ClassType('OldStyleClass', (), _get_class_dict(methods))
def _get_class_dict(methods):
    return dict((method.name, method.get_function())
                for method in methods)

def resets_forge_at_end(func):
    @wraps(func)
    def new_func(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.assertNoMoreCalls()
        self.forge.reset()
    return new_func

class Checkpoint(object):
    called = False
    def trigger(self):
        self.called = True
