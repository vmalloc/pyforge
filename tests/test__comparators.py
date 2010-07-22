from ut_utils import TestCase
from forge import Is, IsA
import cStringIO

class Compared(object):
    def __eq__(self):
        raise NotImplementedError()
    def __ne__(self):
        raise NotImplementedError()    

class IsTest(TestCase):
    def test__valid_equality(self):
        c = Compared()        
        self.assertTrue(Is(c) == c)
    def test__invalid_equality(self):
        c = Compared()
        self.assertFalse(Is(c) == Compared())
    def test__valid_inequality(self):
        c = Compared()
        self.assertTrue(Is(c) != Compared())
    def test__invalid_inequality(self):
        c = Compared()
        self.assertFalse(Is(c) != c)

class IsATest(TestCase):
    def test__valid_equality(self):
        c = Compared()        
        self.assertTrue(IsA(Compared) == c)
    def test__invalid_equality(self):
        c = Compared()
        self.assertFalse(IsA(basestring) == c)
    def test__valid_inequality(self):
        c = Compared()
        self.assertTrue(IsA(basestring) != c)
    def test__invalid_inequality(self):
        c = Compared()
        self.assertFalse(IsA(Compared) != c)
    def test__special_types(self):
        self.assertTrue(IsA(cStringIO.StringIO()) == cStringIO.StringIO())

        
