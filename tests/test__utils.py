from ut_utils import TestCase, ForgeTestCase
from forge.utils import renumerate, EXPECTING
from forge.class_mock_handle import ClassMockHandle

class RenumerateTest(TestCase):
    def test__simple_usage(self):
        self.assertEquals(list(renumerate(list(range(5)))),
                          [(4, 4), (3, 3), (2, 2), (1, 1), (0, 0)])

class EXPECTING_Test(ForgeTestCase):
    def test(self):
        mocked = self.forge.create_wildcard_mock()
        handle = self.forge.create_mock(ClassMockHandle)
        mocked.__forge__ = handle
        handle.expect_setattr("foo", "bar")
        with self.forge.verified_replay_context():
            EXPECTING(mocked).foo = "bar"
