from ut_utils import ForgeTestCase

def _real_function_no_varargs(a, b, c=2):
    raise NotImplementedError()

def _real_function_with_varargs(a, b, c=2, *args, **kwargs):
    raise NotImplementedError()


class FunctionMockRecordReplayTest(ForgeTestCase):
    def test__record_replay(self):
        stub = self.forge.create_function_stub(_real_function_with_varargs)
        self.assertTrue(self.forge.is_recording())
        stub(1, 2, 3)
        self.forge.replay()
        stub(1, 2, 3)
        self.forge.verify()
        
