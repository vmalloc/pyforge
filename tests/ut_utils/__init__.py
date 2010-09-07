from functools import wraps
import types
from forge import Forge

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestCase(unittest.TestCase):
    pass

class ForgeTestCase(TestCase):
    def setUp(self):
        super(ForgeTestCase, self).setUp()
        self.forge = Forge()
    def assertNoMoreCalls(self):
        self.assertEquals(len(self.forge.queue), 0)

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
        exec code in {}, d
        if len(d) != 1:
            raise RuntimeError("More than one function created")
        return d.values()[0]
class ClassMethod(Method):
    def get_function(self):
        return classmethod(super(ClassMethod, self).get_function())
class StaticMethod(Method):
    def get_function(self):
        return staticmethod(super(StaticMethod, self).get_function())

def build_new_style_class(methods=()):
    return type('NewStyleClass', (object,), _get_class_dict(methods))
def build_old_style_class(methods=()):
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
