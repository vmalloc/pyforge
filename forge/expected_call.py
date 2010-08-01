class ExpectedCall(object):
    def __init__(self, target, args, kwargs):
        super(ExpectedCall, self).__init__()
        self.target = target
        self._expected = self.get_signature().get_normalized_args(args, kwargs)
    def get_signature(self):
        return self.target._signature
    def matches_call(self, target, args, kwargs):
        return self.target is target and self.get_signature().get_normalized_args(args, kwargs) == self._expected
