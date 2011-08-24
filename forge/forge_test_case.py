try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase
from .forge import Forge

class ForgeTestCase(TestCase):
    def setUp(self):
        super(ForgeTestCase, self).setUp()
        self.forge = Forge()
    def tearDown(self):
        try:
            self.forge.verify()
        finally:
            self.forge.restore_all_replacements()
        super(ForgeTestCase, self).tearDown()
