from mock_handle import MockHandle

WILDCARD = lambda *args, **kwargs: None

class WildcardMockHandle(MockHandle):
    def _has_method(self, name):
        return True
    def _get_real_method(self, name):
        return WILDCARD
    def has_nonmethod_class_member(self, name):
        return False

