import random
from .ut_utils import ForgeTestCase
from forge.exceptions import UnexpectedCall


class Obj(object):
    def f(self, a, b, c):
        raise NotImplementedError()  # pragma: no cover

    def g(self, value):
        raise NotImplementedError()  # pragma: no cover


class InterleavedTest(ForgeTestCase):
    def setUp(self):
        super(InterleavedTest, self).setUp()
        # make tests deterministic and reproducible...
        random.seed(0)
        self.obj = self.forge.create_mock(Obj)

    def test__interleaved__single_collection(self):
        with self.forge.interleaved_order():
            self.obj.f(1, 2, 3).and_return(2)
            self.obj.f(2, 3, 4).and_return(3)

        self.forge.replay()
        self.assertEquals(self.obj.f(1, 2, 3), 2)
        with self.assertRaises(UnexpectedCall):
            self.obj.f(1, 2, 4)
        self.assertEquals(self.obj.f(2, 3, 4), 3)

    def test__interleaved__two_ordered_nested(self):
        with self.forge.interleaved_order():
            with self.forge.ordered():
                self.obj.f(1, 1, 1).and_return(11)
                self.obj.f(1, 1, 2).and_return(12)
                self.obj.f(1, 1, 3).and_return(13)

            with self.forge.ordered():
                self.obj.f(1, 2, 1).and_return(21)
                self.obj.f(1, 2, 2).and_return(22)
                self.obj.f(1, 2, 3).and_return(23)

        self.forge.replay()

        parallels = [
            [((1, 1, 1), 11), ((1, 1, 2), 12), ((1, 1, 3), 13)],
            [((1, 2, 1), 21), ((1, 2, 2), 22), ((1, 2, 3), 23)]
        ]

        while parallels:
            random.shuffle(parallels)
            thread = parallels[0]

            if len(thread) > 1:
                # try to skip one call...
                with self.assertRaises(UnexpectedCall):
                    self.obj.f(*thread[1][0])

            args, ret = thread.pop(0)
            self.assertEquals(self.obj.f(*args), ret)
            if not thread:
                parallels.pop(0)

    def test__interleaved__zero_context(self):
        with self.forge.interleaved_order():
            pass

        self.forge.replay()
