from forge import Forge

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestCase(unittest.TestCase):
    pass

class ForgeTestCase(TestCase):
    def setUp(self):
        super(ForgeTestCase, self).setUp()
        self.forge = Forge()
