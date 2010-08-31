from ut_utils import ForgeTestCase
from forge import UnauthorizedMemberAccess

class WildcardTest(ForgeTestCase):
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(WildcardTest, self).tearDown()
    def test__wildcard_functions(self):
        wcf = self.forge.create_wildcard_function_stub()
        self._do_all_sorts_of_calls(wcf)
        self.forge.replay()
        self._do_all_sorts_of_calls(wcf)
    def _do_all_sorts_of_calls(self, func):
        func(1, 2, 3)
        func(1, 2)
        func()
        func(a=2)
        func(1, 2, a=2, d=3)
    def test__wildcard_record_replay(self):
        wc = self.forge.create_wildcard_mock()
        wc.f(1, 2, 3)
        wc.g(1, 2, 3, d=4)
        self.forge.replay()
        wc.f(1, 2, 3)
        wc.g(1, 2, 3, d=4)
    def test__wildcard_access_to_unrecorded_methods(self):
        wc = self.forge.create_wildcard_mock()
        self.forge.replay()
        with self.assertRaises(UnauthorizedMemberAccess):
            wc.f
    def test__wildcard_access_to_unrecorded_methods_getattr_in_record(self):
        wc = self.forge.create_wildcard_mock()
        wc.f # no call!
        self.forge.replay()
        wc.f # todo: this shouldn't be ok... to be solved when setattr expectations are added
    def test__setattr_forbidden(self):
        wc = self.forge.create_wildcard_mock()
        wc.a = 2
        self.forge.replay()
        self.assertEquals(wc.a, 2)
        with self.assertRaises(AttributeError):
            wc.a = 2
        with self.assertRaises(AttributeError):
            wc.a = 3
        with self.assertRaises(AttributeError):
            wc.b = 3
