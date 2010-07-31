class ExpectedCall(object):
    def __init__(self, target, args, kwargs):
        super(ExpectedCall, self).__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
    def matches_call(self, target, args, kwargs):
        return target is self.target and self.args == args and self.kwargs == kwargs
