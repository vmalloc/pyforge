from ut_utils import ForgeTestCase
from forge import UnexpectedCall

class ContextManager(object):
    def __enter__(self):
        raise NotImplementedError()
    def __exit__(self, t, v, tb):
        raise NotImplementedError()


class ContextManagerTest(ForgeTestCase):
    def setUp(self):
        super(ContextManagerTest, self).setUp()
        self.obj = self.forge.create_mock(ContextManager)
        self.checkpoint = self.forge.create_function_stub(lambda: None)
    def tearDown(self):
        self.assertEquals(len(self.forge.queue), 0)
        self.forge.verify()
        super(ContextManagerTest, self).tearDown()
    def test__expecting_context(self):
        with self.obj:
            self.checkpoint()
        self.forge.replay()
        with self.obj:
            self.checkpoint()
    def test__expecting_context_with_exception_inside(self):
        with self.obj:
            self.checkpoint()
        my_exception = Exception()
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            with self.obj:
                raise my_exception
        caught = caught.exception
        self.assertIs(caught.expected.target, self.checkpoint)
        self.assertIs(caught.got.target.__forge__.original.im_func, ContextManager.__exit__.im_func)
        self.assertIs(caught.got.args['t'], Exception)
        self.assertIs(caught.got.args['v'], my_exception)
        self.assertIsNotNone(caught.got.args['tb'])
        self.assertEquals(len(self.forge.queue), 2)
        self.forge.reset()
