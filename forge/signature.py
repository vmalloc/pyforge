import inspect
import itertools
from exceptions import SignatureException

NOTHING = object()


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
        self._build_arguments()
    def _iter_args_and_defaults(self, args, defaults):
        defaults = [] if defaults is None else defaults
        filled_defaults = itertools.chain(itertools.repeat(NOTHING, len(args) - len(defaults)), defaults)
        return itertools.izip(args, filled_defaults)

    def _build_arguments(self):
        self.args = []
        args, varargs_name, kwargs_name, defaults = inspect.getargspec(self.func)
        for arg_name, default in self._iter_args_and_defaults(args, defaults):
            self.args.append(Argument(arg_name, default))
        self._varargs_name = varargs_name
        self._kwargs_name = kwargs_name
    def has_variable_args(self):
        return self._varargs_name is not None
    def has_variable_kwargs(self):
        return self._kwargs_name is not None
    def get_normalized_args(self, args, kwargs):
        returned = {}
        self._update_normalized_positional_args(returned, args)
        self._update_normalized_kwargs(returned, kwargs)
        self._check_missing_arguments(returned)
        self._check_unknown_arguments(returned, args, kwargs)
        return returned
    def _update_normalized_positional_args(self, returned, args):
        for our_arg, given_arg in zip(self.args, args):
            returned[our_arg.name] = given_arg
    def _update_normalized_kwargs(self, returned, kwargs):
        for arg_name, arg in kwargs.iteritems():
            if arg_name in returned:
                raise SignatureException("%s is given more than once to %s" % (arg_name, self.func_name))
            returned[arg_name] = arg

    def _check_missing_arguments(self, args_dict):
        required_arguments = set(arg.name for arg in self.args if not arg.has_default())
        missing_arguments = required_arguments - set(args_dict)
        if missing_arguments:
            raise SignatureException("The following arguments were not specified: %s" % ",".join(map(repr, missing_arguments)))
    def _check_unknown_arguments(self, args_dict, args, kwargs):
        if len(args) > len(self.args) and not self.has_variable_args():
            raise SignatureException("%s receives %s positional arguments (%s specified)" % (self.func_name, len(self.args), len(args)))
        unknown = set(args_dict) - set(arg.name for arg in self.args)
        if unknown and not self.has_variable_kwargs():
            raise SignatureException("%s received unknown argument(s): %s" % (self.func_name, ",".join(unknown)))
        


