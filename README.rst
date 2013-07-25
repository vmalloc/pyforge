.. image:: https://secure.travis-ci.org/vmalloc/pyforge.png

What is it?
===========

Forge is a mocking library for Python. It draws most of its inspiration from Mox (http://code.google.com/p/pymox). It is aimed to be simple, but still feature-rich, and provide maximum flexibility for unit testing using the mock approach.

Running Forge's Acceptance Suite
================================
All of Forge's acceptance tests are in the tests/ directory under the root. They require either unittest2 or the built-in unittest module (2.7/3.2 and above).

Running the tests is recommended with the *nosetests* script, but in case you don't have it, the *run_tests* script can be used instead.

Installation
============
Installing forge is pretty much the same as most of the packages you already know

::

 python setup.py install

Usage
=====

Basics
------
Forge mostly creates mock objects and function stubs, but in a variety of flavors. Using Forge always starts with creating a "Mock Manager", with the *Forge* class::

 >>> from forge import Forge
 >>> forge_manager = Forge()

There shouldn't be a real reason for keeping more than one forge manager. What it is typically used for is creating mocks::

 >>> class SomeClass(object):
 ...     def f(self, a, b, c):
 ...         pass
 >>> mock = forge_manager.create_mock(SomeClass)
 >>> mock
 <Mock of 'SomeClass'>

Mock tests usually act in a record-replay manner. You record what you expect your mock to do, and then replay it, while Forge tracks what happens and makes sure it is correct::

 >>> forge_manager.is_recording()
 True
 >>> mock.f(1, 2, 3) # doctest: +ELLIPSIS
 <...>
 >>> mock.f(3, 4, 5) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> forge_manager.is_recording()
 False
 >>> forge_manager.is_replaying()
 True
 >>> mock.f(1, 2, 3)
 >>> mock.f(3, 4, 5)
 >>> forge_manager.verify() # this verifies no more calls are expected

To start over working from scratch, you can always perform::

 >>> forge_manager.reset()

Just like classes yield mocks, regular functions yield stubs, through the use of *Forge.create_function_stub*::

 >>> def some_func(a, b, c):
 ...     pass
 >>> stub = forge_manager.create_function_stub(some_func)

As methods and functions are recorded, their signature is verified against the recorded calls. Upon replay the call must match the original call, so you shouldn't worry too much about accidents concerning the function signature.

To promote niceness, two context managers provide syntactic sugar that structure the test code:

 >>> with forge_manager.record_context():
 ...    mock.f(1, 2, 3) # doctest: +ELLIPSIS
 ...    mock.f(3, 4, 5) # doctest: +ELLIPSIS
 <...>
 >>> with forge_manager.verified_replay_context():
 ...    mock.f(1, 2, 3) # doctest: +ELLIPSIS
 ...    mock.f(3, 4, 5) # doctest: +ELLIPSIS

Failures and Unexpected Events
------------------------------
Whenever an event occurs that was not expected, an exception is raised, explaining what happend::

 >>> stub = forge_manager.create_function_stub(some_func)
 >>> stub(1, 2, 3) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> stub(1, 2, 4) # doctest: +IGNORE_EXCEPTION_DETAIL
 Traceback (most recent call last):
  ...
 UnexpectedCall: Unexpected function called! (Expected: +, Got: -)
 - some_func(a=1, b=2, c=4)
 ?                       ^
 + some_func(a=1, b=2, c=3)
 ?                       ^
 >>> forge_manager.reset()

In some cases this is sufficient, but in case you want a bit more info as to where the calls were recorded and replayed, you can turn on debug info::

 >>> forge_manager.debug.enable()
 >>> stub = forge_manager.create_function_stub(some_func)
 >>> stub(1, 2, 3) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> stub(1, 2, 4) # doctest: +IGNORE_EXCEPTION_DETAIL
 Traceback (most recent call last):
  ...
 UnexpectedCall: Unexpected function called! (Expected: +, Got: -)
 Recorded from ...
 Replayed from ...
 - some_func(a=1, b=2, c=4)
 ?                       ^
 + some_func(a=1, b=2, c=3)
 ?                       ^
 >>> forge_manager.reset()
 >>> forge_manager.debug.disable()

Since sometimes this is a very common pattern, you can also turn on debugging through environment variables, by setting the FORGE_DEBUG environment variable to anything when running your tests.

Expecting Attribute Setting
---------------------------
Setting attributes for mock object is allowed only during record mode. By default, attributes set during replay will trigger an exception.

However, in some cases you want to *expect* an attribute being set at some point of the replay. Due to the hackish nature of the Forge setattr/getattr mechanism, the way to do this is with a dedicated API through the __forge__ handle:

>>> mock = forge_manager.create_mock(SomeClass)
>>> mock.__forge__.expect_setattr("length", 20) # doctest: +ELLIPSIS
<...>
>>> forge_manager.replay()
>>> mock.length = 20
>>> forge_manager.verify()
>>> forge_manager.reset()

You can also set mock object to ignore attribute setting (thus allow all setattrs regardless of nature). This is not recommended, but might sometimes be useful::

>>> mock.__forge__.enable_setattr_during_replay()
>>> forge_manager.replay()
>>> mock.a = 2 # works!
>>> forge_manager.reset()

If you want to simulate a *mock structure*, that is, an object with attributes which are in turn other objects, you can use the *create_mock_with_attrs* API. This is especially concise if you create a shortcut for it:

>>> class A(object): pass
>>> class B(object): pass
>>> class C(object): pass
>>> MOCK = forge_manager.create_mock_with_attrs
>>> result = MOCK(A, b=MOCK(B, c=MOCK(C)))
>>> result.b.c # doctest: +ELLIPSIS
<Mock of 'C'>

Actions
-------
When expecting a call on a stub, you can control what happens *when* the call takes place. Supported cases are:

- controlling the return value::

   my_stub(1, 2, 3).and_return(666)

- calling another function (no arguments)::

   my_stub(1, 2, 3).and_call(callback)

- calling another function with certain arguments/keyword arguments::

   my_stub(1, 2, 3).and_call(callback, args=(100, 200), kwargs={'some_arg':20})

- calling another function (with the arguments of the call)::

   my_stub(1, 2, 3).and_call_with_args(callback)

- raising an exception (happens after all callbacks are fired)::

   my_stub(1, 2, 3).and_raise(MyException())

Comparators
-----------
If you don't know the exact value that the argument to a function is going to get, you sometimes have to use predicates to help you distinguish valid cases from invalid ones. For starters we'll mention that mock objects will only compare 'true' to themselves, so you shouldn't worry about any funky business as far as mock comparison goes.

To complete the picture, if you want to assert all sorts of checks on the arguments you are recording, you can use comparators. For instance, the following doesn't care about which argument is passed to 'name', as long as it is a string::

 my_stub(name=IsA(basestring))

Many comparators exist in Forge:

* ``Is(x)``: compares true only if the argument is *x*
* ``IsA(type)``: compares true only if the argument is of type *type*
* ``RegexpMatches(regexp, [flags])``: compares true only if the argument is a string, and matches *regexp*
* ``Func(f)``: compares true only if *f* returns True for the argument
* ``IsAlmost(value, [places])``: compares true only if the argument is almost identical to *value*, by *places* digits after the floating point
* ``Contains(element)``: compares true only if *element* exists in the argument
* ``StrContains(substring)``: compares true only if *substring* exists in the argument, and the argument is a string
* ``HasKeyValue(key, value)``: compares true only if the argument has *key* as a key, whose value is *value*
* ``HasAttributeValue(attr, value)``: same as HasKeyValue, but for attributes
* ``Anything()``: always compares true
* ``And(...), Or(...), Not(c)``: and, or and a negator for other comparators

Replacing Methods and Functions with Stubs
------------------------------------------
Forge includes a mechanism for installing (and later removing) stubs instead of ordinary methods and functions::

 >>> import time
 >>> forge_manager.replace(time, "time") # doctest: +ELLIPSIS
 <...>
 >>> time.time().and_return(2)
 2
 >>> forge_manager.replay()
 >>> time.time()
 2
 >>> forge_manager.verify()
 >>> forge_manager.restore_all_replacements()
 >>> forge_manager.reset()

 This also works, of course, on methods:

 >>> class MyClass(object):
 ...     def f(self):
 ...         self.g()
 ...     def g(self):
 ...         raise NotImplementedError()
 >>> instance = MyClass()
 >>> forge_manager.replace(instance, "g") # doctest: +ELLIPSIS
 <...>
 >>> instance.g() # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> instance.f()
 >>> forge_manager.verify()
 >>> forge_manager.restore_all_replacements()
 >>> forge_manager.reset()

One can also use the same install mechanism to set a custom value and have it restored along with all stubs::

 >>> class SomeClass(object):
 ...     x = 2
 >>> forge_manager.replace_with(SomeClass, "x", 3)
 3
 >>> SomeClass.x
 3
 >>> forge_manager.restore_all_replacements()
 >>> SomeClass.x
 2

Replacing is also supported within a context, restoring the installed stub upon exit from the context::

 >>> with forge_manager.replacing_context(SomeClass, "x"):
 ...    pass

Ordering
--------
By default, forge verifies that the order in which calls are made in practice is the same as the record flow.
You can, however, control it and create groups in which order does not matter::

 >>> class SomeClass(object):
 ...     def func(self, arg):
 ...        pass
 >>> mock = forge_manager.create_mock(SomeClass)
 >>> mock.func(1) # doctest: +ELLIPSIS
 <...>
 >>> mock.func(2) # doctest: +ELLIPSIS
 <...>
 >>> mock.func(3) # doctest: +ELLIPSIS
 ... # so far order must be kept
 <...>
 >>> with forge_manager.any_order(): # doctest: +ELLIPSIS
 ...     mock.func(4)
 ...     mock.func(5)
 <...>
 <...>
 >>> mock.func(6) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> mock.func(1)
 >>> mock.func(2)
 >>> mock.func(3)
 >>> mock.func(5) # ok!
 >>> mock.func(4) # also ok!
 >>> mock.func(6)
 >>> forge_manager.verify()
 >>> forge_manager.reset()


You can always nest ordering groups, by using *ordered*, *any_order* and *interleaved_order* (see below) ::

 >>> with forge_manager.any_order(): # doctest: +ELLIPSIS
 ...     mock.func(4)
 ...     with forge_manager.ordered():
 ...         mock.func(5)
 ...         mock.func(6)
 ...     mock.func(7)
 <...>
 <...>
 <...>
 <...>

In the example above, func(5) and func(6) will be asserted to occur in this specific order, but the group can appear anywhere among func(4) and func(7).

 >>> forge_manager.replay()
 >>> for i in (5, 6, 7, 4):
 ...     _ = mock.func(i)
 >>> forge_manager.verify()
 >>> forge_manager.reset()


In the context of nested ordering groups, the *interleaved* ordering may come in handy when working with coroutines/greenlets::

 >>> class SomeClass(object):
 ...     def foo(self, arg):
 ...        pass
 ...     def bar(self, arg):
 ...        pass
 >>> mock = forge_manager.create_mock(SomeClass)
 >>> with forge_manager.interleaved_order(): # doctest: +ELLIPSIS
 ...     with forge_manager.ordered():
 ...         mock.foo(1)
 ...         mock.foo(2)
 ...     with forge_manager.ordered():
 ...         mock.bar(1)
 ...         mock.bar(2)
 <...>
 <...>
 <...>
 <...>
 >>> forge_manager.replay()
 >>> mock.foo(1)
 >>> mock.bar(1)
 >>> mock.foo(2)
 >>> mock.bar(2)
 >>> forge_manager.verify()
 >>> forge_manager.reset()

The expectation above will work with following sequence as well:

 >>> with forge_manager.interleaved_order(): # doctest: +ELLIPSIS
 ...     with forge_manager.ordered():
 ...         mock.foo(1)
 ...         mock.foo(2)
 ...     with forge_manager.ordered():
 ...         mock.bar(1)
 ...         mock.bar(2)
 <...>
 <...>
 <...>
 <...>
 >>> forge_manager.replay()
 >>> mock.bar(1)
 >>> mock.bar(2)
 >>> mock.foo(1)
 >>> mock.foo(2)
 >>> forge_manager.verify()
 >>> forge_manager.reset()


Whenever
--------
Sometimes you intend for a function to be called zero or more times, regardless of timing, and return a certain value (or raise an exception). There are ugly ways to do this::

 >>> class MyObj(object):
 ...     def f(self):
 ...         pass
 >>> m = forge_manager.create_mock(MyObj)
 >>> m.f = lambda: 2 # yuck!

And of course the downside is that:

 * the fact that f exists doesn't get verified. Also its signature is not verified with this method.
 * lambda's are ugly, and it gets nastier when you want to use exceptions.

*whenever()* to the rescue - it is a method that can be called on expected methods, causing the call to be accepted, signature checked and acted upon. However, unlike regular recordings, it expects the call 0 or more times, at any point - so it achieves the same effect::

 >>> m = forge_manager.create_mock(MyObj)
 >>> m.f().whenever().and_return(2)
 2
 >>> forge_manager.replay()
 >>> m.f()
 2
 >>> m.f()
 2
 >>> forge_manager.verify()
 >>> forge_manager.reset()

Multiple *whenever()* recordings can be specified with different parameters, which results in a form of "pattern matching" for the requested calls (each call signature will result in a different return value).

An alternative syntax exists for *whenever()* for easier readability::

 >>> class Obj(object):
 ...     def f(self, value):
 ...         pass
 >>> m = forge_manager.create_mock(Obj)
 >>> m.f.when(2).then_return(3)
 3
 >>> forge_manager.replay()
 >>> m.f(2)
 3
 >>> forge_manager.verify()
 >>> forge_manager.reset()

.. note:: whenever() calls always apply to the ordering group in which they were recorded. This means that once an order group is cleared, all of the *whenever*s recorded in it are automatically "forgotten", and will no longer be accepted on replay.

Wildcard Mocks
--------------
Although not recommended, sometimes you just want a mock that accepts anything during record, and just verifies that you stick to it in replay. This is useful for prototyping an interface that doesn't exist yet. This is done in Forge by using *wildcard mocks*::

 >>> mock = forge_manager.create_wildcard_mock()
 >>> mock
 <<Wildcard>>
 >>> stub = forge_manager.create_wildcard_function_stub()
 >>> stub
 <Stub for '<<Wildcard>>'>
 >>> mock.f() # doctest: +ELLIPSIS
 <...>
 >>> mock.g(1, 2, 3, d=4) # doctest: +ELLIPSIS
 <...>
 >>> stub() # doctest: +ELLIPSIS
 <...>
 >>> stub(1, 2, 3, d=4) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> mock.f()
 >>> mock.g(1, 2, 3, d=4)
 >>> stub()
 >>> stub(1, 2, 3, d=4)
 >>> forge_manager.reset()

Class Mocks
-----------
Sometimes you would like to simulate the behavior of a class, and not an object. Forge allows to do this with the *create_class_mock* API::

 >>> class MyClass(object):
 ...     def __init__(self, a, b, c):
 ...         pass
 ...     def regular_method(self):
 ...         pass
 ...     @classmethod
 ...     def some_class_method(cls):
 ...         pass
 ...     @staticmethod
 ...     def some_static_method():
 ...         pass
 >>> class_mock = forge_manager.create_class_mock(MyClass)
 >>> class_mock
 <Class mock of 'MyClass'>
 >>> class_mock.regular_method() # doctest: +IGNORE_EXCEPTION_DETAIL
 Traceback (most recent call last):
 SignatureException: ...
 >>> class_mock.some_class_method() # doctest: +ELLIPSIS
 <...>
 >>> class_mock.some_static_method() # doctest: +ELLIPSIS
 <...>
 >>> fake_new_instance = forge_manager.create_mock(MyClass)
 >>> class_mock(1, 2, 3).and_return(fake_new_instance) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> class_mock.some_class_method()
 >>> class_mock.some_static_method()
 >>> assert class_mock(1, 2, 3) is fake_new_instance
 >>> forge_manager.verify()
 >>> forge_manager.reset()

Hybrid Mocks
------------
Suppose you have a class like the following::

 >>> class File(object):
 ...     def __init__(self, filename):
 ...         self.f = open(filename, "rb")
 ...     def read(self, size):
 ...         raise NotImplementedError()
 ...     def log(self, buffer):
 ...         raise NotImplementedError()
 ...     def read_and_log(self, size):
 ...         data = self.read(size)
 ...         self.log(data)
 ...         return data

Now, suppose you want to write a test for read_and_log, while mimicking the behavior of read() and log(). This is quite common, because sometimes methods in your classes have lots of side effects which are hard to plumb during test writing. One easy approach would be to create a File object and to replace read() and log() with stubs (see above). This is fine, but the problem is with the class construction, which opens a file for reading.

In some cases, constructors (especially in legacy code to which you add tests) do lots of things that are hard to stub, or that are likely to change thus breaking any stubbing work you might install. For this case Forge has hybrid mocks::

 >>> mock = forge_manager.create_hybrid_mock(File)
 >>> mock.read(20).and_return("data") # doctest: +ELLIPSIS
 '...'
 >>> mock.log("data") # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> assert mock.read_and_log(20) == "data"
 >>> forge_manager.verify()
 >>> forge_manager.reset()

Hybrid mocks are, well, hybrid. They behave as regular mocks during record, but calling any method during replay that hasn't been recorded will invoke the original method on the mock, thus testing it in an isolated environment.

A class equivalent also exists::

 >>> class SomeClass(object):
 ...     def __init__(self, parameter):
 ...         raise NotImplementedError()
 ...     @classmethod
 ...     def constructor(cls):
 ...         return cls(1)

 >>> mock = forge_manager.create_hybrid_class_mock(SomeClass)
 >>> expected_return_value = forge_manager.create_sentinel()
 >>> mock(1).and_return(expected_return_value) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> got_return_value = mock.constructor()
 >>> got_return_value is expected_return_value
 True
