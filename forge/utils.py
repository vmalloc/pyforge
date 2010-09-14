from types import *

def renumerate(collection):
    for index in xrange(len(collection) - 1, -1, -1):
        yield (index, collection[index])

### object predicates
def is_method(obj):
    return isinstance(obj, MethodType)
def is_bound_method(obj):
    return is_method(obj) and obj.im_self is not None
def is_function(obj):
    return isinstance(obj, FunctionType) or isinstance(obj, BuiltinFunctionType)
def is_class(obj):
    return isinstance(obj, type) or isinstance(obj, ClassType)
def is_class_method(obj):
    im_self = getattr(obj, 'im_self', None)
    if im_self is None:
        return False
    return is_class(im_self)
