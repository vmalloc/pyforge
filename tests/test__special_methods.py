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
            Method("__getitem__(self, item)"),
            Method('__delitem__(self, item)'),
            Method('__iter__(self)'),
            Method('__call__(self, a, b, c)')
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
    def test__getitem_explicit(self):
        self.obj.__getitem__(2).and_return(3)
        self.forge.replay()
        self.assertEquals(self.obj[2], 3)
    def test__getitem_implicit(self):
        self.obj[2].and_return(3)
        self.forge.replay()
        self.assertEquals(self.obj[2], 3)
    def test__getitem_mismatch(self):
        self.obj[2].and_return(3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            self.obj[3]
        self.assertEquals(len(self.forge.queue), 1)
        self.forge.reset()
    def test__delitem_explicit(self):
        self.obj.__delitem__(2)
        self.forge.replay()
        del self.obj[2]
    def test__delitem_implicit(self):
        del self.obj[2]
        self.forge.replay()
        del self.obj[2]
    def test__delitem_mismatch(self):
        del self.obj[2]
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            del self.obj[3]
        self.assertEquals(len(self.forge.queue), 1)
        self.forge.reset()
    def test__iter(self):
        expected_result = [1, 3, 4, 5]
        self.obj.__iter__().and_return(iter(expected_result))
        self.forge.replay()
        l = [x for x in self.obj]
        self.assertEquals(l, expected_result)
    def test__call(self):
        self.obj(1, 2, c=3).and_return(5)
        self.forge.replay()
        self.assertEquals(self.obj(1, 2, c=3), 5)
    def test__call_mismatch(self):
        self.obj(1, 2, c=3).and_return(5)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            self.obj(1, 2, c=4)
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

    def test__special_method_absence(self):
        for statement in self._get_invalid_statements():
            with self.assertRaises(TypeError):
                exec statement

    def _get_invalid_statements(self):
        return [
            'len(self.obj)',
            'self.obj.__setitem__(1, 2)',
            'self.obj[1] = 2',
            'self.obj.__getitem__(1)',
            'self.obj[1]',
            'del self.obj[1]',
            'self.obj.__delitem__(1)',
            'list(self.obj)',
            'iter(self.obj)',
            'self.obj(1, 2, 3)',
            'self.obj()'
            ]

class NewStyleSpecialMethodsAbsenceTest(_SpecialMethodAbsenceTest):
    def setUp(self):
        super(NewStyleSpecialMethodsAbsenceTest, self).setUp()
        self.obj = self.forge.create_mock(build_new_style_class())
class OldStyleSpecialMethodsAbsenceTest(_SpecialMethodAbsenceTest):
    def setUp(self):
        super(OldStyleSpecialMethodsAbsenceTest, self).setUp()
        self.obj = self.forge.create_mock(build_old_style_class())
