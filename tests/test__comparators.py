import itertools
import re
from .ut_utils import TestCase, BinaryObjectClass
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
            self.assertIsInstance(str(a), str)
            self.assertEqual(str(a), repr(a))

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
        yield IsA(str), "hey"
        yield IsA(type(BinaryObjectClass())), BinaryObjectClass()
    def _get_unequal_pairs(self):
        yield IsA(Compared), "hey"
        yield IsA(str), Compared()
        yield IsA(type(BinaryObjectClass())), object()
        yield IsA(BinaryObjectClass), BinaryObjectClass
        yield IsA(BinaryObjectClass()), BinaryObjectClass()

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
        yield Contains("hey"), ["hey", "there"]
        yield Contains("a", "b"), "abcdefg"
        yield Contains("a", "b"), ["a", "b"]
    def _get_unequal_pairs(self):
        yield Contains("a"), "hello"
        yield Contains("bla"), object()
        yield Contains(2), [1, 3, 5]
        yield Contains("hey"), ["hello", "world"]
        yield Contains("a", "b"), "a"
        yield Contains("a", "b"), "b"
        yield Contains("a", "b", "d"), ["a", "b"]

class StrContainsTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield StrContains("a"), "laugh"
        yield StrContains("bl"), "able"
        yield StrContains("a", "b"), "able"
    def _get_unequal_pairs(self):
        yield StrContains("hey"), ["hey", "there"]
        yield StrContains("a"), "hello"
        yield StrContains("bla"), object()
        yield StrContains(2), [1, 2, 3]
        yield StrContains(2), [1, 3, 5]
        yield StrContains("hey"), ["hello", "world"]
        yield StrContains("a", "b"), "a"
        yield StrContains("a", "b"), ["a", "b"]

class HasKeyValueTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield HasKeyValue('a', 1), dict(a=1, b=2)
        yield HasKeyValue(1, 2), [0, 2, 0, 0]
    def _get_unequal_pairs(self):
        yield HasKeyValue('a', 1), {}
        yield HasKeyValue('a', 1), dict(a=2)
        yield HasKeyValue('a', 1), []
        yield HasKeyValue('a', 1), object()
        yield HasKeyValue(0, 1), [0, 0, 0]

class HasAttributeValueTest(_ComparatorTest):
    class Object(object):
        a = 2
        b = 3
    def _get_equal_pairs(self):
        Object = self.Object
        yield HasAttributeValue('a', 2), Object
        yield HasAttributeValue('b', 3), Object()
    def _get_unequal_pairs(self):
        Object = self.Object
        for obj in (Object, Object()):
            yield HasAttributeValue('a', 3), obj
        yield HasAttributeValue('bla', 2), Object()
        yield HasAttributeValue('bloop', 2), dict(bloop=2)

class AnythingTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield Anything(), object
        yield Anything(), object()
        yield Anything(), 2
        yield Anything(), "bla"
        yield Anything(), Anything()
    def _get_unequal_pairs(self):
        return ()

class AndTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield And(IsA(str), Contains('a')), "Boa"
        yield And(IsA(str), Contains('a'), Contains('g')), "Bga"
        yield And(IsA(int)), 2
    def _get_unequal_pairs(self):
        yield And(IsA(str), Contains('a')), 2
        yield And(IsA(str), Contains('a'), Contains('g')), "Boa"
        yield And(IsA(int)), "a"
    def test__empty_and(self):
        with self.assertRaises(TypeError):
            And()
class OrTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield Or(IsA(str), IsA(int)), "a"
        yield Or(Anything(), IsA(str)), 2
        yield Or(IsA(str), Anything()), 2
    def _get_unequal_pairs(self):
        yield Or(IsA(str), IsA(int)), 2.0
    def test__empty_or(self):
        with self.assertRaises(TypeError):
            Or()

class NotTest(_ComparatorTest):
    def _get_equal_pairs(self):
        yield Not(IsA(int)), "a"
    def _get_unequal_pairs(self):
        yield Not(Anything()), 2
        yield Not(Anything()), object()

