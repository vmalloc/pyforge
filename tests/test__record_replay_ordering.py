from .ut_utils import ForgeTestCase
from forge import UnexpectedCall, ExpectedEventsNotFound
from forge.python3_compat import basestring
import random

class OrderingTest(ForgeTestCase):
    def setUp(self):
        super(OrderingTest, self).setUp()
        self.stub = self.forge.create_function_stub(lambda arg: None)
class StrictOrderingTest(OrderingTest):
    def test__strict_ordering(self):
        self.stub(1)
        self.stub(2)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(2)
        self.assertIs(caught.exception.got.target, self.stub)
        self.assertEquals(len(caught.exception.expected), 1)
        self.assertIs(caught.exception.expected[0].target, self.stub)
        self.forge.reset()

class EmptyGroupTest(OrderingTest):
    def test__empty_group_with_initial_ordered(self):
        self._test__empty_group(True, True, True)
        self._test__empty_group(True, True, False)
    def test__empty_group_with_initial_unordered(self):
        self._test__empty_group(True, False, True)
        self._test__empty_group(True, False, False)
    def test__empty_group_without_initial_ordered(self):
        self._test__empty_group(False, True, True)
        self._test__empty_group(False, True, False)
    def test__empty_group_without_initial_unordered(self):
        self._test__empty_group(False, False, True)
        self._test__empty_group(False, False, False)
    def _test__empty_group(self, with_initial_recording, ordered, success):
        if with_initial_recording:
            self.stub(0)
        if ordered:
            context = self.forge.ordered
        else:
            context = self.forge.any_order
        with context():
            pass
        self.stub(1)
        self.stub(2)
        self.forge.replay()
        if with_initial_recording:
            self.stub(0)
        if success:
            self.stub(1)
            self.stub(2)
            self.forge.verify()
        else:
            with self.assertRaises(UnexpectedCall):
                self.stub(2)
        self.forge.reset()

class OrderGroupsTest(OrderingTest):
    def setUp(self):
        super(OrderGroupsTest, self).setUp()
        with self.forge.any_order():
            self.stub(0)
            self.stub(1)
        self.stub(2)
        self.stub(3)
        with self.forge.any_order():
            self.stub(4)
            self.stub(5)
        self.forge.replay()
    def test__as_recorded(self):
        for i in range(6):
            self.stub(i)
        self.forge.verify()
    def test__not_as_recorded(self):
        self.stub(1)
        self.stub(0)
        self.stub(2)
        self.stub(3)
        self.stub(5)
        self.stub(4)
        self.forge.verify()

# class EmptyGroupTest(OrderingTest):
#     def test__empty_ordered_group(self):
#         self._test__empty_group(self.forge.ordered)
#     def test__empty_unordered_group(self):
#         self._test__empty_group(self.forge.any_order)
#     def _test__empty_group(self, context):
#         with context():
#             pass
#         self.stub(1)
#         self.forge.replay()
#         self.stub(1)
#         self.forge.verify()

class OrderingGroupExceptionFormatting(OrderingTest):
    def test__unexpected_call(self):
        with self.forge.any_order():
            self.stub(1)
            self.stub(2)
            self.stub(3)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(4)
        self.assertIsInstance(caught.exception.expected, list)
        self.assertIsInstance(str(caught.exception), basestring)
        self.assertIsInstance(repr(caught.exception), basestring)
        self.forge.reset()


class OrderedOrderedGroupTest(OrderingTest):
    def test__ordered_ordered(self):
        self.stub(0)
        self.stub(1)
        with self.forge.ordered():
            self.stub(2)
            self.stub(3)
        self.stub(4)
        self.forge.replay()
        for i in range(5):
            self.stub(i)
        self.forge.verify()

    def test__ordered_ordered__unexpected(self):
        self.stub(0)
        with self.forge.ordered():
            self.stub(1)
            self.stub(2)
        self.stub(3)
        self.forge.replay()
        self.stub(0)
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(2)
        self.assertIsInstance(caught.exception.expected, list)
        self.assertIsInstance(str(caught.exception), basestring)
        self.assertIsInstance(repr(caught.exception), basestring)
        self.forge.reset()


class OrderedAnyOrderGroupTest(OrderingTest):
    def setUp(self):
        super(OrderedAnyOrderGroupTest, self).setUp()
        self.stub(0)
        with self.forge.any_order():
            self.stub(1)
            self.stub(2)
            with self.forge.ordered():
                self.stub('a')
                self.stub('b')
            self.stub(3)
        self.stub(4)
        self.forge.replay()

    def test__as_recorded(self):
        for n in (0, 1, 2, 'a', 'b', 3, 4):
            self.stub(n)
        self.forge.verify()

    def test__not_as_recorded(self):
        for n in (0, 'a', 'b', 1, 2, 3, 4):
            self.stub(n)
        self.forge.verify()

    def test__not_as_recorded_2(self):
        for n in (0, 3, 1, 'a', 'b', 2, 4):
            self.stub(n)
        self.forge.verify()

    def test__not_as_recorded_3(self):
        for n in (0, 'a', 'b', 2, 3, 1, 4):
            self.stub(n)
        self.forge.verify()

    def test__break_inner_ordered__unexpected(self):
        for n in (0, 1, 'a'):
            self.stub(n)
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(2)
        self.assertIsInstance(caught.exception.expected, list)
        self.assertIsInstance(str(caught.exception), basestring)
        self.assertIsInstance(repr(caught.exception), basestring)
        self.forge.reset()


class OrderedAnyOrder2GroupTest(OrderingTest):
    def setUp(self):
        super(OrderedAnyOrder2GroupTest, self).setUp()
        self.stub(0)
        with self.forge.any_order():
            self.stub(1)
            self.stub(2)
            with self.forge.ordered():
                self.stub('a')
                self.stub('b')
            self.stub(3)
            with self.forge.ordered():
                self.stub('c')
                self.stub('d')
        self.stub(4)
        self.forge.replay()

    def test__as_recorded(self):
        for n in (0, 1, 2, 'a', 'b', 3, 'c', 'd', 4):
            self.stub(n)
        self.forge.verify()

    def test__not_as_recorded(self):
        for n in (0, 'c', 'd', 1, 'a', 'b', 2, 3, 4):
            self.stub(n)
        self.forge.verify()

    def test__break_inner_ordered__unexpected(self):
        for n in (0, 1, 'c', 'd'):
            self.stub(n)
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub('b')
        self.assertIsInstance(caught.exception.expected, list)
        self.assertIsInstance(str(caught.exception), basestring)
        self.assertIsInstance(repr(caught.exception), basestring)
        self.forge.reset()

class OrderedAnyOrderOrderedGroupTest(OrderingTest):
    def setUp(self):
        super(OrderedAnyOrderOrderedGroupTest, self).setUp()
        self.stub(0)
        with self.forge.any_order():
            self.stub(1)
            self.stub(2)
            with self.forge.ordered():
                self.stub('a')
                with self.forge.any_order():
                    self.stub('!')
                    self.stub('@')
                self.stub('b')
            self.stub(3)
        self.stub(4)
        self.forge.replay()

    def test__as_recorded(self):
        for n in (0, 1, 2, 'a', '!', '@', 'b', 3, 4):
            self.stub(n)
        self.forge.verify()

    def test__not_as_recorded(self):
        for n in (0, 'a', '@', '!', 'b', 3, 2, 1, 4):
            self.stub(n)
        self.forge.verify()

