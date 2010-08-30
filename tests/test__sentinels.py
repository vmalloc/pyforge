from ut_utils import ForgeTestCase

class SentinelTest(ForgeTestCase):
    def test__sentinel_equality(self):
        s1 = self.forge.create_sentinel()
        s2 = self.forge.create_sentinel()
        self.assertNotEqual(s1, s2)
        self.assertEqual(s1, s1)
        self.assertEqual(s2, s2)
    def test__sentinel_name(self):
        s1 = self.forge.create_sentinel('s1')
        self.assertIn('s1', str(s1))
        self.assertIn('s1', repr(s1))

