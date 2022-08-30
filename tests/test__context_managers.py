import types
from .ut_utils import ForgeTestCase
from forge import UnexpectedCall
from forge import UnexpectedSetattr

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
        self.assertTrue(self.forge.queue.is_empty())
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
        self.assertEqual(len(caught.expected), 1)
        self.assertIs(caught.expected[0].target, self.checkpoint)
        self.assertIsSameMethod(caught.got.target.__forge__.original,
                                ContextManager.__exit__)
        self.assertIs(caught.got.args['t'], Exception)
        self.assertIs(caught.got.args['v'], my_exception)
        self.assertIsNotNone(caught.got.args['tb'])
        self.assertEqual(len(self.forge.queue), 2)
        self.forge.reset()
    def test__expecting_context_with_unexpected_call_inside(self):
        stub = self.forge.create_function_stub(lambda arg: None)
        with self.obj:
            stub(1)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            with self.obj:
                stub(2)
        caught = caught.exception
        self.assertEqual(len(caught.expected), 1)
        self.assertIs(caught.expected[0].target, stub)
        self.assertIs(caught.got.target, stub)
        self.assertIs(caught.expected[0].args['arg'], 1)
        self.assertIs(caught.got.args['arg'], 2)
        self.assertEqual(len(self.forge.queue), 2)
        self.forge.reset()
    def test__expecting_context_with_unexpected_setattr_inside(self):
        with self.obj:
            pass
        self.forge.replay()
        with self.assertRaises(UnexpectedSetattr) as caught:
            with self.obj:
                self.obj.a = 2
        caught = caught.exception
        self.assertEqual(len(caught.expected), 1)
        self.assertIs(caught.expected[0].target, self.obj.__forge__.get_attribute('__exit__'))
        self.assertEqual(len(caught.expected[0].args), 3)
        self.assertTrue(all(x is None for x in caught.expected[0].args.values()))
        self.assertIs(caught.got.target, self.obj)
        self.assertEqual(caught.got.name, 'a')
        self.assertEqual(caught.got.value, 2)
        self.assertEqual(len(self.forge.queue), 1)
        self.forge.reset()
    def test__enter_returning_value(self):
        self.obj.__enter__().and_return(2)
        self.checkpoint()
        self.obj.__exit__(None, None, None)
        self.forge.replay()
        with self.obj as value:
            self.checkpoint()
        self.assertEqual(value, 2)
    def assertIsSameMethod(self, a, b):
        if not isinstance(a, types.FunctionType):
            a = a.__func__
        if not isinstance(b, types.FunctionType):
            b = b.__func__
        return a is b
