from ut_utils import ForgeTestCase
from ut_utils import build_new_style_class
from ut_utils import build_old_style_class
from forge import UnexpectedCall

class _SpecialMethodsTest(ForgeTestCase):
    def setUp(self):
        super(_SpecialMethodsTest, self).setUp()
        self.obj = self.forge.create_mock(self.CTOR([

            ]))
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(_SpecialMethodsTest, self).tearDown()
    def test__len(self):
        self.obj.__len__().AndReturn(2)
        self.forge.replay()
        self.assertEquals(len(self.obj), 2)
    def test__setitem_explicit(self):
        self.obj.__setitem__('a', 'b')
        self.forge.replay()
        self.obj['a'] = 'b'
    def test__setitem_implicit(self):
        self.obj['a'] = 'b'
        self.forge.replay()
        self.obj['a'] = 'b'
    def test__setitem_mismatch(self):
        self.obj['a'] = 'b'
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            self.obj['a'] = 'c'

class NewStyleSpecialMethodsTest(_SpecialMethodsTest):
    CTOR = staticmethod(build_new_style_class)
class OldStyleSpecialMethodsTest(_SpecialMethodsTest):
    CTOR = staticmethod(build_old_style_class)
