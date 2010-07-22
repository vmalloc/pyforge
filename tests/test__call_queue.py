from ut_utils import TestCase
from forge.call_queue import CallQueue

class CallQueueTest(TestCase):
    def setUp(self):
        super(CallQueueTest, self).setUp()
        self.queue = CallQueue()
        self.obj = object()
        self.assertEmpty()
    def assertEmpty(self):
        self.assertEquals(len(self.queue), 0)
        self.assertEquals(list(self.queue), [])
    def test__push(self):
        self.queue.push(self.obj)
        self.assertEquals(len(self.queue), 1)
        self.assertIs(list(self.queue)[0], self.obj)
    def test__pop(self):
        self.test__push()
        
    def test__reset(self):
        self.test__push()
        self.queue.reset()
        self.assertEmpty()
