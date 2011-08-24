from .ut_utils import ForgeTestCase
from forge.exceptions import UnexpectedCall

class Obj(object):
    def f(self, a, b, c):
        raise NotImplementedError() # pragma: no cover

class WheneverTest(ForgeTestCase):
    def setUp(self):
        super(WheneverTest, self).setUp()
        self.obj = self.forge.create_mock(Obj)
    def test__whenever_verifies_arguments(self):
        self.obj.f(1, 2, 3).whenever().and_return(2)
        self.forge.replay()
        self.assertEquals(self.obj.f(1, 2, 3), 2)
        with self.assertRaises(UnexpectedCall):
            self.obj.f(1, 2, 4)
        self.assertEquals(self.obj.f(1, 2, 3), 2)
    def test__whenever_accepts_zero_times(self):
        self.obj.f(1, 2, 3).whenever().and_return(2)
        self.forge.replay()
    def test__whenever_and_raise(self):
        e = Exception()
        self.obj.f(1, 2, 3).whenever().and_raise(e)
        self.forge.replay()
        with self.assertRaises(Exception) as caught:
            self.obj.f(1, 2, 3)
        self.assertIs(caught.exception, e)
    def test__whenever_with_multiple_groups(self):
        call = self.obj.f(1, 2, 3)
        self.obj.f(1, 1, 1).and_return(1)
        with self.forge.any_order():
            self.obj.f(2, 2, 2).and_return(2)
        self.obj.f(3, 3, 3).and_return(3)
        call.whenever().and_return("hey")
        self.forge.replay()
        for i in range(3):
            self.assertEquals("hey", self.obj.f(1, 2, 3))
        self.assertEquals(1, self.obj.f(1, 1, 1))
        self.assertEquals("hey", self.obj.f(1, 2, 3))
        self.assertEquals(2, self.obj.f(2, 2, 2))
        self.assertEquals(3, self.obj.f(3, 3, 3))
        self.assertEquals("hey", self.obj.f(1, 2, 3))
