import types
import itertools
import platform

IS_PY3 = (platform.python_version() >= '3')

if IS_PY3:
    iteritems = dict.items
    xrange = range
    basestring = str
else:
    iteritems = dict.iteritems
    from __builtin__ import xrange, basestring

def izip(*args, **kwargs):
    if IS_PY3:
        return zip(*args, **kwargs)
    return itertools.izip(*args, **kwargs)

def build_instance_method(function, instance, cls):
    if IS_PY3:
        return types.MethodType(function, instance)
    return types.MethodType(function, instance, cls)
def build_unbound_instance_method(function, cls):
    if IS_PY3:
        return types.MethodType(function, cls)
    return types.MethodType(function, None, cls)

