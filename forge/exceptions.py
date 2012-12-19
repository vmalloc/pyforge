from difflib import Differ
from .queued_object import QueuedObject


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

UNEXPECTED_FUNCTION_CALLED_STR = "Unexpected function called!"
UNEXPECTED_SETATTR_STR = "Unexpected attribute set!"
DIFF_DESCRIPTION_STR = "(Expected: +, Got: -)"


class UnexpectedEvent(ForgeException):
    def __init__(self, expected, got):
        super(UnexpectedEvent, self).__init__()
        self.expected = expected
        self.got = got

    def __str__(self):
        returned = self._getTitle()
        returned += " %s\n" % DIFF_DESCRIPTION_STR
        debug_info = self._get_debug_info()
        if debug_info:
            returned += debug_info
        returned += self._get_diff_string()
        return returned

    def _get_debug_info(self):
        returned = ""
        returned += self._get_expected_caller_infos()
        returned += self._get_got_caller_infos()
        return returned

    def _get_expected_caller_infos(self):
        return self._get_caller_infos("Recorded", self.expected)

    def _get_got_caller_infos(self):
        return self._get_caller_infos("Replayed", self.got)

    def _get_caller_infos(self, verb, list_or_single):
        if not isinstance(list_or_single, list):
            list_or_single = [list_or_single]
        returned = ""
        for option in list_or_single:
            if option and option.caller_info:
                returned += "%s from %s\n" % (verb, option.caller_info)
        return returned

    def _get_diff_string(self):
        got_string = self._get_got_string()
        expected_string = self._get_expected_string()
        if got_string == expected_string:
            return "- %s\n+ %s" % (expected_string, got_string)
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
        if isinstance(x, list):
            if len(x) == 1:
                x = x[0]
            elif len(x) == 0:
                x = None
        if x is None:
            return "<< None >>"
        if not isinstance(x, QueuedObject):
            return str(x)
        return x.describe()


class UnexpectedCall(UnexpectedEvent):
    @classmethod
    def _getTitle(cls):
        return UNEXPECTED_FUNCTION_CALLED_STR


class UnexpectedSetattr(UnexpectedEvent):
    @classmethod
    def _getTitle(cls):
        return UNEXPECTED_SETATTR_STR


class ExpectedEventsNotFound(ForgeException):
    def __init__(self, events):
        super(ExpectedEventsNotFound, self).__init__()
        if type(events) is not list:
            raise ValueError("Expected events must be a list")
        self.events = events

    def __str__(self):
        return "Expected events not found:\n%s" % "\n".join(map(str, self.events))


class InvalidEntryPoint(ForgeException):
    pass
