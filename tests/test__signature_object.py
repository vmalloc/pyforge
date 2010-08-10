import time
from ut_utils import TestCase
from forge.signature import FunctionSignature
from forge.exceptions import SignatureException, InvalidKeywordArgument

# no named tuples for python 2.5 compliance...
class ExpectedArg(object):
    def __init__(self, name, has_default, default=None):
        self.name = name
        self.has_default = has_default
        self.default = default

class SignatureTest(TestCase):
    def _assert_argument_names(self, sig, names):
        self.assertEquals([arg.name for arg in sig.args], names)

    def _test_function_signature(self,
        func,
        expected_signature,
        has_varargs=False,
        has_varkwargs=False
        ):
        sig = FunctionSignature(func)

        self.assertEquals(len(expected_signature), len(sig.args))
        for expected_arg, arg in zip(expected_signature, sig.args):
            if isinstance(expected_arg, tuple):
                expected_arg = ExpectedArg(*expected_arg)
            self.assertEquals(expected_arg.name,
                              arg.name)
            self.assertEquals(expected_arg.has_default,
                              arg.has_default())
            if expected_arg.has_default:
                self.assertEquals(expected_arg.default, arg.default)
        self.assertEquals(sig.has_variable_kwargs(), has_varkwargs)
        self.assertEquals(sig.has_variable_args(), has_varargs)

    def test__simple_functions(self):
        def f(a, b, c):
            pass
        self._test_function_signature(f,
                                      [('a', False),
                                       ('b', False),
                                       ('c', False)])

    def test__kwargs(self):
        def f(a, b, c=2):
            pass
        def f_args(a, b, c=2, *args):
            pass
        def f_kwargs(a, b, c=2, **kwargs):
            pass
        def f_args_kwargs(a, b, c=2, *args, **kwargs):
            pass
        lambda_args_kwargs = lambda a, b, c=2, *args, **kwargs: None
        sig = [('a', False),
               ('b', False),
               ('c', True, 2)]
        self._test_function_signature(f, sig)
        self._test_function_signature(f_args, sig, has_varargs=True)
        self._test_function_signature(f_kwargs, sig, has_varkwargs=True)
        self._test_function_signature(f_args_kwargs, sig, has_varargs=True, has_varkwargs=True)
        self._test_function_signature(lambda_args_kwargs, sig, has_varargs=True, has_varkwargs=True)


    def test__normalizing_args(self):
        def f(a, b, c=2, *args, **kwargs):
            pass
        sig = FunctionSignature(f)

        self.assertEquals(dict(a=1, b=2),
                          sig.get_normalized_args((1, 2), {}))
        self.assertEquals(dict(a=1, b=2, c=3),
                          sig.get_normalized_args((1, 2, 3), {}))
        self.assertEquals(dict(a=1, b=2, c=3),
                          sig.get_normalized_args((1, 2), dict(c=3)))
        self.assertEquals({'a':1, 'b':2, 'c':3, 0:4, 1:5, 'kwarg':6},
                          sig.get_normalized_args((1, 2, 3, 4, 5), dict(kwarg=6)))

        with self.assertRaises(SignatureException):
            sig.get_normalized_args((1, 2), dict(a=1))
        with self.assertRaises(SignatureException):
            sig.get_normalized_args((), {})
    def test__normalizing_args_no_kwargs(self):
        def f(a, *args):
            raise NotImplementedError()
        sig = FunctionSignature(f)
        self.assertEquals({'a': 1, 0: 2}, sig.get_normalized_args((1, 2), {}))
    def test__normalizing_args_strict_functions(self):
        def strict_f(a, b, c):
            pass

        strict_sig = FunctionSignature(strict_f)

        with self.assertRaises(SignatureException):
            strict_sig.get_normalized_args((), {})
        with self.assertRaises(SignatureException):
            strict_sig.get_normalized_args((1, 2, 3, 4), {})
        with self.assertRaises(SignatureException):
            strict_sig.get_normalized_args((), dict(d=4))
    def test__normalizing_method_args(self):
        class SomeClass(object):
            def f(self, a, b, c):
                raise NotImplementedError()
        class SomeOldStyleClass:
            def f(self, a, b, c):
                raise NotImplementedError()
        for cls in (SomeClass, SomeOldStyleClass):
            sig = FunctionSignature(cls.f)
            self.assertEquals(
                dict(a=1, b=2, c=3),
                sig.get_normalized_args((1, 2, 3), {})
                )
            self.assertEquals(
                dict(a=1, b=2, c=3),
                sig.get_normalized_args((1,), dict(c=3, b=2))
                )

    def test__normalizing_kwargs_with_numbers(self):
        # this is supported in python, but interferes with the arg-normalizing logic
        sig = FunctionSignature(lambda *args, **kwargs: None)
        with self.assertRaises(InvalidKeywordArgument):
            sig.get_normalized_args((), {1:2})

    def test__is_binding_needed(self):
        def f():
            raise NotImplementedError()
        def f_with_self_arg(self):
            raise NotImplementedError()
        self.assertFalse(FunctionSignature(f).is_binding_needed())
        self.assertFalse(FunctionSignature(f_with_self_arg).is_binding_needed())
        class SomeClass(object):
            def f_without_self():
                raise NotImplementedError()
            def f(self):
                raise NotImplementedError()
            def f_with_args(self, a, b, c):
                raise NotImplementedError()
            def f_with_first_argument_not_self(bla):
                raise NotImplementedError()
        class SomeOldStyleClass:
            def f_without_self():
                raise NotImplementedError()
            def f(self):
                raise NotImplementedError()
            def f_with_args(self, a, b, c):
                raise NotImplementedError()
            def f_with_first_argument_not_self(bla):
                raise NotImplementedError()
        for cls in (SomeClass, SomeOldStyleClass):
            self.assertTrue(FunctionSignature(cls.f_without_self).is_binding_needed())
            self.assertTrue(FunctionSignature(cls.f_with_args).is_binding_needed())
            self.assertTrue(FunctionSignature(cls.f_with_first_argument_not_self).is_binding_needed())

class BinaryFunctionSignatureTest(TestCase):
    def test__dummy_signature(self):
        sig = FunctionSignature(time.time)
        self.assertEquals(sig.args, [])
        self.assertTrue(sig.has_variable_args())
        self.assertTrue(sig.has_variable_kwargs())
