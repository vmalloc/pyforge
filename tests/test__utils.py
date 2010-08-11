from ut_utils import TestCase
from forge.utils import renumerate

class RenumerateTest(TestCase):
    def test__simple_usage(self):
        self.assertEquals(list(renumerate(range(5))),
                          [(4, 4), (3, 3), (2, 2), (1, 1), (0, 0)])
