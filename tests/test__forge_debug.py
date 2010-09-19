import os
from ut_utils import TestCase
from forge import Forge
from forge.caller_info import CallerInfo

class ForgeDebugTest(TestCase):
    def assertDebugOff(self, forge):
        self.assertFalse(forge.debug.is_enabled())
        self.assertIsNone(forge.debug.get_caller_info())
    def assertDebugOn(self, forge):
        self.assertTrue(forge.debug.is_enabled())
        self.assertIsInstance(forge.debug.get_caller_info(), CallerInfo)
    def test__debug_states(self):
        f = Forge()
        self.assertDebugOff(f)
        f.debug.enable()
        self.assertDebugOn(f)
        f.debug.disable()
        self.assertDebugOff(f)
    def test__debug_disable_enable(self):
        prev_value = os.environ.get('FORGE_DEBUG', None)
        os.environ['FORGE_DEBUG'] = "1"
        try:
            f = Forge()
            self.assertDebugOn(f)
        finally:
            if prev_value is None:
                os.environ.pop('FORGE_DEBUG')
            else:
                os.environ['FORGE_DEBUG'] = prev_value
