import time
from .ut_utils import TestCase
from forge.signature import FunctionSignature
from forge.exceptions import SignatureException, InvalidKeywordArgument, FunctionCannotBeBound

# no named tuples for python 2.5 compliance...
class ExpectedArg(object):
    def __init__(self, name, has_default, default=None):
        self.name = name
        self.has_default = has_default
        self.default = default

class SignatureTest(TestCase):
    def _assert_argument_names(self, sig, names):
        self.assertEquals([arg.name for arg in sig._args], names)

    def _test_function_signature(self,
        func,
        expected_signature,
        has_varargs=False,
        has_varkwargs=False
        ):
        sig = FunctionSignature(func)

        self.assertEquals(len(expected_signature), len(sig._args))
        self.assertEquals(len(expected_signature), sig.get_num_args())
        for expected_arg, arg in zip(expected_signature, sig._args):
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

    def test__normalizing_kwargs_with_numbers(self):
        # this is supported in python, but interferes with the arg-normalizing logic
        sig = FunctionSignature(lambda *args, **kwargs: None)
        with self.assertRaises(InvalidKeywordArgument):
            sig.get_normalized_args((), {1:2})

    def test__is_method_and_is_bound(self):
        def f():
            raise NotImplementedError()
        def f_with_self_arg(self):
            raise NotImplementedError()
        self.assertFalse(FunctionSignature(f_with_self_arg).is_bound_method())
        self.assertFalse(FunctionSignature(f).is_bound_method())
        self.assertFalse(FunctionSignature(f_with_self_arg)._args[0].has_default())
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
            self.assertFalse(FunctionSignature(cls.f).is_bound_method())
            self.assertFalse(FunctionSignature(cls.f_with_args).is_bound_method())
            self.assertFalse(FunctionSignature(cls.f_with_first_argument_not_self).is_bound_method())
            self.assertTrue(FunctionSignature(cls().f).is_bound_method())
            self.assertTrue(FunctionSignature(cls().f_with_args).is_bound_method())
            self.assertTrue(FunctionSignature(cls().f_with_first_argument_not_self).is_bound_method())
    def test__is_class_method(self):
        class New(object):
            @classmethod
            def class_method(cls):
                raise NotImplementedError()
            def regular_method(self):
                raise NotImplementedError()
        class Old(object):
            @classmethod
            def class_method(cls):
                raise NotImplementedError()
            def regular_method(self):
                raise NotImplementedError()
        self.assertTrue(FunctionSignature(New.class_method).is_class_method())
        self.assertTrue(FunctionSignature(Old.class_method).is_class_method())
        self.assertFalse(FunctionSignature(New.regular_method).is_class_method())
        self.assertFalse(FunctionSignature(Old.regular_method).is_class_method())
    def test__copy(self):
        f = FunctionSignature(lambda a, b: 2)
        f2 = f.copy()
        self.assertIsNot(f, f2)
        self.assertIsNot(f._args, f2._args)

class BinaryFunctionSignatureTest(TestCase):
    def test__binary_global_function(self):
        sig = FunctionSignature(time.time)
        self.assertEquals(sig._args, [])
        self.assertTrue(sig.has_variable_args())
        self.assertTrue(sig.has_variable_kwargs())
    def test__object_method_placeholders(self):
        class SomeObject(object):
            pass
        sig = FunctionSignature(SomeObject.__ge__)
