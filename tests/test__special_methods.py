from .ut_utils import BinaryObjectClass
from functools import partial
from .ut_utils import ForgeTestCase
from .ut_utils import build_new_style_class
from .ut_utils import build_old_style_class
from .ut_utils import Method
from forge import UnexpectedCall
from forge.python3_compat import IS_PY3

class _SpecialMethodsTest(ForgeTestCase):
    def setUp(self):
        super(_SpecialMethodsTest, self).setUp()
        self.obj = self.forge.create_mock(self.CTOR([
            Method("__len__(self)"),
            Method("__setitem__(self, item, value)"),
            Method("__getitem__(self, item)"),
            Method('__delitem__(self, item)'),
            Method('__iter__(self)'),
            Method('__call__(self, a, b, c)'),
            Method('__contains__(self, item)'),
            Method('__nonzero__(self)'),
            Method('__bool__(self)'),
            ]))
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(_SpecialMethodsTest, self).tearDown()
    def test__len(self):
        self.obj.__len__().and_return(2)
        self.forge.replay()
        self.assertEqual(len(self.obj), 2)
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
        self.assertEqual(len(self.forge.queue), 1)
        self.forge.reset()
    def test__getitem_explicit(self):
        self.obj.__getitem__(2).and_return(3)
        self.forge.replay()
        self.assertEqual(self.obj[2], 3)
    def test__getitem_implicit(self):
        self.obj[2].and_return(3)
        self.forge.replay()
        self.assertEqual(self.obj[2], 3)
    def test__getitem_mismatch(self):
        self.obj[2].and_return(3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            self.obj[3]
        self.assertEqual(len(self.forge.queue), 1)
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
        self.assertEqual(len(self.forge.queue), 1)
        self.forge.reset()
    def test__iter(self):
        expected_result = [1, 3, 4, 5]
        self.obj.__iter__().and_return(iter(expected_result))
        self.forge.replay()
        l = [x for x in self.obj]
        self.assertEqual(l, expected_result)
    def test__call(self):
        self.obj(1, 2, c=3).and_return(5)
        self.forge.replay()
        self.assertEqual(self.obj(1, 2, c=3), 5)
    def test__call_mismatch(self):
        self.obj(1, 2, c=3).and_return(5)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            self.obj(1, 2, c=4)
        self.assertEqual(len(self.forge.queue), 1)
        self.forge.reset()
    def test__contains_explicit(self):
        self.obj.__contains__(2).and_return(True)
        self.obj.__contains__(2).and_return(False)
        self.forge.replay()
        self.assertTrue(2 in self.obj)
        self.assertFalse(2 in self.obj)
    def test__contains_mismatch(self):
        self.obj.__contains__(2).and_return(True)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall):
            3 in self.obj
        self.assertEqual(len(self.forge.queue), 1)
        self.forge.reset()
    def test__boolean(self):
        if IS_PY3:
            self.obj.__bool__().and_return(False)
        else:
            self.obj.__nonzero__().and_return(False)
        self.forge.replay()
        self.assertFalse(self.obj)


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
                exec(statement)

    def test__boolean(self):
        self.assertTrue(self.obj)

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
            'self.obj()',
            '3 in self.obj'
            ]

class NewStyleSpecialMethodsAbsenceTest(_SpecialMethodAbsenceTest):
    def setUp(self):
        super(NewStyleSpecialMethodsAbsenceTest, self).setUp()
        self.obj = self.forge.create_mock(build_new_style_class())
class OldStyleSpecialMethodsAbsenceTest(_SpecialMethodAbsenceTest):
    def setUp(self):
        super(OldStyleSpecialMethodsAbsenceTest, self).setUp()
        self.obj = self.forge.create_mock(build_old_style_class())

class CallCornerCasesTest(ForgeTestCase):
    def test__callable_metaclass(self):
        class Object(object):
            class __metaclass__(type):
                def __call__(self, a, b, c):
                    return 2
        obj = self.forge.create_mock(Object)
        with self.assertRaises(TypeError):
            obj(1, 2, 3)
    def test__non_callable_binary_classes(self):
        obj = self.forge.create_mock(type(BinaryObjectClass()))
        with self.assertRaises(TypeError):
            obj(1, 2, 3)
    def test__callable_binary_classes(self):
        obj = self.forge.create_mock(partial)
        obj(1, 2, 3)
        self.forge.replay()
        obj(1, 2, 3)

