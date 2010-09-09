from mock_handle import MockHandle
from dtypes import WILDCARD_FUNCTION
from exceptions import UnauthorizedMemberAccess

class WildcardMockHandle(MockHandle):
    def _has_method(self, name):
        return True
    def _get_real_method(self, name):
        return WILDCARD_FUNCTION
    def _check_unrecorded_method_getting(self, name):
        raise UnauthorizedMemberAccess(self.mock, name)
    def has_nonmethod_class_member(self, name):
        return False
    def _check_special_method_call(self, *_, **__):
        pass

