from difflib import Differ
from queued_object import QueuedObject

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
        returned += " (Expected: +, Got: -)\n"
        returned += self._get_diff_string()
        return returned
    def _get_diff_string(self):
        diff = Differ().compare(
            [self._get_got_string()],
            [self._get_expected_string()],
            )
        return "\n".join(line.strip() for line in diff)
    def _get_expected_string(self):
        return self._get_description_string(self.expected)
    def _get_got_string(self):
        return self._get_description_string(self.got)
    def _get_description_string(self, x):
        if x is None:
            return "<< None >>"
        if not isinstance(x, QueuedObject):
            return str(x)
        return x.describe()
class UnexpectedCall(UnexpectedEvent):
    @classmethod
    def _getTitle(cls):
        return "Unexpected function called!"
class UnexpectedSetattr(UnexpectedEvent):
    @classmethod
    def _getTitle(cls):
        return "Unexpected attribute set!"

class ExpectedEventsNotFound(ForgeException):
    def __init__(self, events):
        super(ExpectedEventsNotFound, self).__init__()
        self.events = events
    def __str__(self):
        return "Expected events not found:\n%s" % "\n".join(map(str, self.events))

class InvalidEntryPoint(ForgeException):
    pass

