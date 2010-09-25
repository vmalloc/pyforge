from .exceptions import SignatureException

class BoundSignatureAdapter(object):
    def __init__(self, signature, obj):
        super(BoundSignatureAdapter, self).__init__()
        if signature.is_bound_method():
            raise SignatureException("%s is already bound!" % self.stub)
        self._signature = signature
        self._obj = obj
    def is_bound(self):
        return True
    def get_normalized_args(self, args, kwargs):
        new_args = [self._obj]
        new_args.extend(args)
        returned = self._signature.get_normalized_args(new_args, kwargs)
        returned.pop(self._get_self_arg_name())
        return returned
    def _get_self_arg_name(self):
        arg_names = list(self._signature.get_arg_names())
        if arg_names:
            return arg_names[0]
        return 0
