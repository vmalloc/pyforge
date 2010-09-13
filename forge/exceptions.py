class ForgeException(Exception):
    pass

class SignatureException(ForgeException):
    pass

class InvalidKeywordArgument(SignatureException):
    pass

class FunctionCannotBeBound(SignatureException):
    pass

class ConflictingActions(ForgeException):
    pass

class MockObjectUnhashable(ForgeException):
    pass

class CannotMockException(ForgeException):
    pass
class CannotMockFunctions(CannotMockException):
    pass

class UnexpectedEvent(ForgeException):
    def __init__(self, expected, got):
        super(UnexpectedEvent, self).__init__()
        self.expected = expected
        self.got = got
    def __str__(self):
        returned = self._getTitle()
        returned += "\n Expected: %s" % (self.expected,)
        returned += "\n Got: %s" % (self.got,)
        return returned
class UnexpectedCall(UnexpectedEvent):
    @classmethod
    def _getTitle(cls):
        return "Unexpected function called!"
class UnexpectedSetattr(UnexpectedEvent):
    @classmethod
    def _getTitle(cls):
        return "Unexpected attribute set!"

class ExpectedCallsNotFound(ForgeException):
    def __init__(self, calls):
        super(ExpectedCallsNotFound, self).__init__()
        self.calls = calls
    def __str__(self):
        return "Expected calls not found:\n%s" % "\n".join(map(str, self.calls))

class InvalidEntryPoint(ForgeException):
    pass

