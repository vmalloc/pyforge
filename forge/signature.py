import types
import inspect
import itertools
from exceptions import SignatureException, InvalidKeywordArgument
from numbers import Number
from dtypes import NOTHING

class Argument(object):
    def __init__(self, name, default=NOTHING):
        super(Argument, self).__init__()
        self.name = name
        self.default = default
    def has_default(self):
        return self.default is not NOTHING

class FunctionSignature(object):
    def __init__(self, func):
        super(FunctionSignature, self).__init__()
        self.func = func
        self.func_name = func.__name__
        self._can_be_called_as_method = False
        self._build_arguments()
    def _iter_args_and_defaults(self, args, defaults):
        defaults = [] if defaults is None else defaults
        filled_defaults = itertools.chain(itertools.repeat(NOTHING, len(args) - len(defaults)), defaults)
        return itertools.izip(args, filled_defaults)

    def is_first_argument_self(self):
        return type(self.func) in (types.MethodType,)
    def can_be_called_as_method(self):
        return self._can_be_called_as_method
    def _build_arguments(self):
        self.args = []
        if self._can_function_be_inspected(self.func):
            args, varargs_name, kwargs_name, defaults = inspect.getargspec(self.func)
        else:
            args = []
            varargs_name = 'args'
            kwargs_name = 'kwargs'
            defaults = []
        if self.is_first_argument_self():
            self._can_be_called_as_method = len(args) > 0
            args = args[1:]
        for arg_name, default in self._iter_args_and_defaults(args, defaults):
            self.args.append(Argument(arg_name, default))
        self._varargs_name = varargs_name
        self._kwargs_name = kwargs_name
    def _can_function_be_inspected(self, func):
        return type(func) not in [
            types.BuiltinFunctionType,
            types.BuiltinMethodType,
            ]
    def has_variable_args(self):
        return self._varargs_name is not None
    def has_variable_kwargs(self):
        return self._kwargs_name is not None
    def get_normalized_args(self, args, kwargs):
        returned = {}
        self._update_normalized_positional_args(returned, args)
        self._update_normalized_kwargs(returned, kwargs)
        self._check_missing_arguments(returned)
        self._check_unknown_arguments(returned)
        return returned
    def _update_normalized_positional_args(self, returned, args):
        argument_names = [arg.name for arg in self.args]
        argument_names.extend(range(len(args) - len(self.args)))
        for arg_name, given_arg in zip(argument_names, args):
            returned[arg_name] = given_arg
        
    def _update_normalized_kwargs(self, returned, kwargs):
        for arg_name, arg in kwargs.iteritems():
            if not isinstance(arg_name, basestring):
                raise InvalidKeywordArgument("Invalid keyword argument %r" % (arg_name,))
            if arg_name in returned:
                raise SignatureException("%s is given more than once to %s" % (arg_name, self.func_name))
            returned[arg_name] = arg

    def _check_missing_arguments(self, args_dict):
        required_arguments = set(arg.name for arg in self.args if not arg.has_default())
        missing_arguments = required_arguments - set(args_dict)
        if missing_arguments:
            raise SignatureException("The following arguments were not specified: %s" % ",".join(map(repr, missing_arguments)))
    def _check_unknown_arguments(self, args_dict):
        positional_arg_count = len([arg_name for arg_name in args_dict if isinstance(arg_name, Number)])
        if positional_arg_count and not self.has_variable_kwargs():
            raise SignatureException("%s receives %s positional arguments (%s specified)" % (self.func_name, len(self.args), len(self.args) + positional_arg_count))
        unknown = set(args_dict) - set(arg.name for arg in self.args)
        if unknown and not self.has_variable_kwargs():
            raise SignatureException("%s received unknown argument(s): %s" % (self.func_name, ",".join(unknown)))
        


