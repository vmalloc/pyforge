from .ut_utils import ForgeTestCase
from forge import UnexpectedSetattr

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
    def test__wildcard_function_names(self):
        wc = self.forge.create_wildcard_function_stub('some_name')
        self.assertIn('some_name', str(wc))
        self.assertIn('some_name', repr(wc))
    def test__wildcard_access_to_unrecorded_methods(self):
        wc = self.forge.create_wildcard_mock()
        self.forge.replay()
        with self.assertRaises(AttributeError):
            wc.f
    def test__wildcard_access_to_unrecorded_methods_getattr_in_record(self):
        wc = self.forge.create_wildcard_mock()
        wc.f # no call!
        self.forge.replay()
        with self.assertRaises(AttributeError):
            wc.f # todo: this shouldn't be ok... to be solved when setattr expectations are added
    def test__setattr_forbidden(self):
        wc = self.forge.create_wildcard_mock()
        wc.a = 2
        self.forge.replay()
        self.assertEqual(wc.a, 2)
        with self.assertRaises(UnexpectedSetattr):
            wc.a = 2
        with self.assertRaises(UnexpectedSetattr):
            wc.a = 3
        with self.assertRaises(UnexpectedSetattr):
            wc.b = 3
    def test__expect_setattr(self):
        wc = self.forge.create_wildcard_mock()
        wc.__forge__.expect_setattr("a", 2)
        self.forge.replay()
        wc.a = 2
        self.assertEqual(wc.a, 2)
    def test__repr(self):
        name = 'some_name'
        wc = self.forge.create_wildcard_mock(name)
        self.assertIn(name, str(wc))
        self.assertIn(name, repr(wc))
    def test__method_repr(self):
        wc = self.forge.create_wildcard_mock()
        m = wc.method_with_specific_name
        self.assertTrue("method_with_specific_name" in repr(m))
        self.assertTrue("method_with_specific_name" in str(m))
    def test__special_methods_ok(self):
        wc = self.forge.create_wildcard_mock()
        f = self.forge.create_wildcard_function_stub()
        with wc:
            f()
        wc.__len__().and_return(666)
        wc.__iter__().and_return(iter(range(10)))
        self.forge.replay()
        with wc:
            f()
        self.assertEqual(len(wc), 666)
        self.assertEqual([x for x in wc], list(range(10)))
