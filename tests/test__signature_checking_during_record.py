from .ut_utils import ForgeTestCase
from forge import SignatureException

class call(object):
    def __init__(self, *args, **kwargs):
        self.func = args[0]
        self.args = args[1:]
        self.kwargs = kwargs

class SignatureCheckingTest(ForgeTestCase):
    def test__good_record(self):
        for good_call in self._iterate_valid_calls():
            stub = self.forge.create_function_stub(good_call.func)
            self.assertTrue(self.forge.is_recording())
            stub(*good_call.args, **good_call.kwargs)
            self.forge.replay()
            stub(*good_call.args, **good_call.kwargs)
            self.forge.verify()
            self.forge.reset()
    def test__signature_checking_on_record(self):
        for invalid_call in self._iterate_invalid_calls():
            stub = self.forge.create_function_stub(invalid_call.func)
            self.assertTrue(self.forge.is_recording())
            with self.assertRaises(SignatureException):
                stub(*invalid_call.args, **invalid_call.kwargs)

    def _iterate_valid_calls(self):
        def f():
            raise NotImplementedError()
        yield call(f)
        def f(a, b, c):
            raise NotImplementedError()
        yield call(f, 1, 2, 3)
        yield call(f, a=1, b=2, c=3)
        yield call(f, 1, 2, c=3)

        def f(a, b, c=2):
            raise NotImplementedError()
        yield call(f, 1, 2, 3)
        yield call(f, a=1, b=2, c=3)
        yield call(f, 1, 2)

        def f(a, b, c=2, *args):
            raise NotImplementedError()
        yield call(f, 1, 2, 3)
        yield call(f, 1, 2, 3, 4, 5)
        yield call(f, 1, 2, c=5)

        def f(a, b, c=2, **kwargs):
            raise NotImplementedError()
        yield call(f, 1, 2, 3)
        yield call(f, 1, 2, 3, d=5)
        yield call(f, 1, 2, c=2, d=5)

        def f(a, b, c=2, *args, **kwags):
            raise NotImplementedError()
        yield call(f, 1, 2, 3, 4, 5)
        yield call(f, 1, 2, 3, 4, 5, d=5, e=8)
    def _iterate_invalid_calls(self):
        def f():
            raise NotImplementedError()
        yield call(f, 2)
        yield call(f, c=3)

        def f(a, b, c):
            raise NotImplementedError()
        yield call(f)
        yield call(f, 1)
        yield call(f, 1, 2)
        yield call(f, 1, 2, 3, 4)
        yield call(f, 1, c=3)

        def f(a, b, c=2):
            raise NotImplementedError()
        yield call(f)
        yield call(f, 1)
        yield call(f, 1, 2, 3, 4)
        yield call(f, c=5)
        yield call(f, 1, c=5)
        def f(a, b, c=2, *args):
            raise NotImplementedError()
        yield call(f, 1, 2, d=5)
        yield call(f, 1, 2, 3, c=5)
        yield call(f, 1, 2, a=1)

        def f(a, b, c=2, **kwargs):
            raise NotImplementedError()
        yield call(f, 1, 2, 3, c=5)
        yield call(f, 1, 2, 3, 4)
        yield call(f, 1, c=2, d=5)

        def f(a, b, c=2, *args, **kwags):
            raise NotImplementedError()
        yield call(f, 1)
        yield call(f, 1, 2, 3, 4, 5, c=4)

