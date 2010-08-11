from ut_utils import TestCase
from forge import Is, IsA, RegexpMatches
import cStringIO
import re

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
