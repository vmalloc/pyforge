from ut_utils import ForgeTestCase
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
