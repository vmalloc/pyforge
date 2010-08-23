from ut_utils import ForgeTestCase
from forge import ConflictingActions
from forge.dtypes import NOTHING

class ActionsTest(ForgeTestCase):
    def setUp(self):
        super(ActionsTest, self).setUp()
        self.stub = self.forge.create_function_stub(lambda *args, **kwargs: None)
    def test__return_value(self):
        rv = self.stub(1, 2, 3).and_return(666)
        self.assertEquals(rv, 666)
        self.forge.replay()
        self.assertEquals(666, self.stub(1, 2, 3))
        self.assertNoMoreCalls()
        self.forge.verify()
    def test__raised_exception(self):
        raised = Exception()
        rv = self.stub(1, 2, 3).and_raise(raised)
        self.assertIs(rv, raised)
        self.forge.replay()
        with self.assertRaises(Exception) as caught:
            self.stub(1, 2, 3)
        self.assertIs(caught.exception, raised)
        self.assertNoMoreCalls()
        self.forge.verify()
    def test__conflicting_actions(self):
        expected_call = self.stub(1, 2, 3)
        expected_call.and_return(2)
        with self.assertRaises(ConflictingActions):
            expected_call.and_raise(Exception())
        #conflict should not affect existing expectations
        self.assertEquals(expected_call._return_value, 2)
        self.assertIs(expected_call._raised_exception, NOTHING)

        expected_call = self.stub(1, 2, 3)
        exc = Exception()
        expected_call.and_raise(exc)
        with self.assertRaises(ConflictingActions):
            expected_call.and_return(2)
                #conflict should not affect existing expectations
        self.assertIs(expected_call._return_value, NOTHING)
        self.assertIs(expected_call._raised_exception, exc)
    def test__and_call(self):
        return_value = 666
        cp = Checkpoint()
        rv = self.stub(1, 2, 3).and_call(cp.trigger).and_return(return_value)
        self.assertEquals(rv, return_value)
        self.forge.replay()
        rv = self.stub(1, 2, 3)
        self.assertEquals(rv, return_value)
        self.assertTrue(cp.called)
    def test__and_call_with_args(self):
        return_value = 666
        cp = Checkpoint()
        def trigger(*args, **kwargs):
            self.assertEquals(args, (1, 2, 3))
            self.assertEquals(kwargs, dict(d=4))
            cp.trigger()
        rv = self.stub(1, 2, 3, d=4).and_call_with_args(trigger).and_return(return_value)
        self.assertEquals(rv, return_value)
        self.forge.replay()
        rv = self.stub(1, 2, 3, d=4)
        self.assertEquals(rv, return_value)
        self.assertTrue(cp.called)

class Checkpoint(object):
    called = False
    def trigger(self):
        self.called = True
