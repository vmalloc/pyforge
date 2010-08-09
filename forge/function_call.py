from dtypes import NOTHING
from exceptions import ConflictingActions

class FunctionCall(object):
    def __init__(self, target, args, kwargs):
        super(FunctionCall, self).__init__()
        self.target = target
        self.args = self.get_signature().get_normalized_args(args, kwargs)
        self._call_funcs = []
        self._call_funcs_with_args = []
        self._return_value = NOTHING
        self._raised_exception = NOTHING
    def get_signature(self):
        return self.target._signature
    def matches_call(self, target, args, kwargs):
        return self.target is target and self.get_signature().get_normalized_args(args, kwargs) == self.args
    def __str__(self):
        return "<Function call: %s(%s)" % (self.target, self._get_argument_string())
    def _get_argument_string(self):
        args = ["%s=%s" % (arg_name, value) for arg_name, value in sorted(self.args.iteritems())
                if isinstance(arg_name, basestring)]
        args.extend(str(value) for arg_name, value in sorted((k, v) for k, v in self.args.iteritems()
                                                        if not isinstance(k, basestring)))
        return ", ".join(args)

    def and_call(self, func):
        self._call_funcs.append(func)
        return self
    def and_call_with_args(self, func):
        self._call_funcs_with_args.append(func)
        return self
    
    def and_raise(self, exc):
        if self._return_value is not NOTHING:
            raise ConflictingActions()
        self._raised_exception = exc
        return exc

    def and_return(self, rv):
        if self._raised_exception is not NOTHING:
            raise ConflictingActions()
        self._return_value = rv
        return rv
    def do_side_effects(self, args, kwargs):
        for call_func in self._call_funcs:
            call_func()
        for call_func in self._call_funcs_with_args:
            call_func(*args, **kwargs)
        if self._raised_exception is not NOTHING:
            raise self._raised_exception
    def get_return_value(self):        
        if self._return_value is not NOTHING:
            return self._return_value
        return None


