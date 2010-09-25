from types import *

def renumerate(collection):
    for index in range(len(collection) - 1, -1, -1):
        yield (index, collection[index])

### object predicates
def is_bound_method(obj):
    return isinstance(obj, MethodType) and obj.__self__ is not None
def is_function(obj):
    return isinstance(obj, FunctionType) or isinstance(obj, BuiltinFunctionType)
def is_class(obj):
    return isinstance(obj, type)
def is_class_method(obj):
    if not is_bound_method(obj):
        return False
    return is_class(obj.__self__)
