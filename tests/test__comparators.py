import cStringIO
import itertools
import re
from ut_utils import TestCase
from forge.comparators import *

class Compared(object):
    def __eq__(self):
        raise NotImplementedError()
    def __ne__(self):
        raise NotImplementedError()

class _ComparatorTest(TestCase):
    def test__valid_equality(self):
        for a, b in self._get_equal_pairs():
            self.assertTrue(a == b)
    def test__invalid_equality(self):
        for a, b in self._get_unequal_pairs():
            self.assertFalse(a == b)
    def test__valid_inequality(self):
        for a, b in self._get_unequal_pairs():
            self.assertTrue(a != b)
    def test__invalid_inequality(self):
        for a, b in self._get_equal_pairs():
            self.assertFalse(a != b)
    def test__representation(self):
        for a, _ in itertools.chain(self._get_equal_pairs(), self._get_unequal_pairs()):
            self.assertIsInstance(a, Comparator)
            self.assertIsInstance(str(a), basestring)
            self.assertEquals(str(a), repr(a))

class IsTest(_ComparatorTest):
    def _get_equal_pairs(self):
        c = Compared()
        yield Is(c), c
    def _get_unequal_pairs(self):
        c = Compared()
        yield Is(c), Compared()
        yield Is(c), 2

class IsATest(_ComparatorTest):
    def _get_equal_pairs(self):
        c = Compared()
        yield IsA(Compared), c
        yield IsA(basestring), "hey"
        IsA(cStringIO.StringIO()), cStringIO.StringIO()
    def _get_unequal_pairs(self):
        yield IsA(Compared), "hey"
        yield IsA(basestring), Compared()
        IsA(cStringIO.StringIO()), object()

class RegexpMatchesTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield RegexpMatches(".+"), "hey"
        yield RegexpMatches(r"hey \S+"), "hey there"
        yield RegexpMatches(r"hello", re.I), "hEllO"
    def _get_unequal_pairs(self):
        yield RegexpMatches(r"hello \S+"), "hey there"
        yield RegexpMatches(r"hello"), 2

class FuncTest(_ComparatorTest):
    def _get_equal_pairs(self):
        obj = object()
        yield Func(lambda o: o is obj), obj
        yield Func(lambda o: True), None
    def _get_unequal_pairs(self):
        obj = object()
        for other in (None, 2, "hello"):
            yield Func(lambda o: o is obj), other
        yield Func(lambda o: False), "hello"

class IsAlmostTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield IsAlmost(3, 3), 3.0002
        yield IsAlmost(3), 3.00000002
    def _get_unequal_pairs(self):
        yield IsAlmost(3, 3), 3.02
        yield IsAlmost(3), 3.02
        yield IsAlmost(3), "hey"

class ContainsTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield Contains("a"), "laugh"
        yield Contains("bl"), "able"
        yield Contains(2), [1, 2, 3]
    def _get_unequal_pairs(self):
        yield Contains("a"), "hello"
        yield Contains("bla"), object()
        yield Contains(2), [1, 3, 5]

