from ut_utils import ForgeTestCase
from ut_utils import build_new_style_class
from ut_utils import build_old_style_class
from ut_utils import Method
from forge import UnexpectedCall

class _SpecialMethodsTest(ForgeTestCase):
    def setUp(self):
        super(_SpecialMethodsTest, self).setUp()
        self.obj = self.forge.create_mock(self.CTOR([
            Method("__len__(self)"),
            Method("__setitem__(self, item, value)"),
            ]))
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(_SpecialMethodsTest, self).tearDown()
    def test__len(self):
        self.obj.__len__().and_return(2)
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
        self.assertEquals(len(self.forge.queue), 1)
        self.forge.reset()

class NewStyleSpecialMethodsTest(_SpecialMethodsTest):
    CTOR = staticmethod(build_new_style_class)
class OldStyleSpecialMethodsTest(_SpecialMethodsTest):
    CTOR = staticmethod(build_old_style_class)

class _SpecialMethodAbsenceTest(ForgeTestCase):
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(_SpecialMethodAbsenceTest, self).tearDown()
    def test__len_absence(self):
        with self.assertRaises(TypeError):
            self.obj.__len__()
        with self.assertRaises(TypeError):
            len(self.obj)
    def test__setitem_absence(self):
        with self.assertRaises(TypeError):
            self.obj.__setitem__('x', 'y')
        with self.assertRaises(TypeError):
            self.obj['x'] = 'y'

class NewStyleSpecialMethodsAbsenceTest(_SpecialMethodAbsenceTest):
    def setUp(self):
        super(NewStyleSpecialMethodsAbsenceTest, self).setUp()
        self.obj = self.forge.create_mock(build_new_style_class())
class OldStyleSpecialMethodsAbsenceTest(_SpecialMethodAbsenceTest):
    def setUp(self):
        super(OldStyleSpecialMethodsAbsenceTest, self).setUp()
        self.obj = self.forge.create_mock(build_old_style_class())
