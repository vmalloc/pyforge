class ForgeException(Exception):
    pass

class SignatureException(ForgeException):
    pass

class UnexpectedCall(ForgeException):
    pass

class ExpectedCallsNotFound(ForgeException):
    def __init__(self, calls):
        super(ExpectedCallsNotFound, self).__init__()
        self.calls = calls
    def __str__(self):
        return "Expected calls not found:\n%s" % "\n".join(map(str, self.calls))

