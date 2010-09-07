What is it?
-----------
Forge is a mocking library for Python. It draws most of its inspiration from Mox (http://code.google.com/p/pymox). It is aimed to be simple, but still feature-rich, and provide maximum flexibility for unit testing using the mock approach.

Installation
------------
Installing forge is pretty much the same as most of the packages you already know

::

 python setup.py install

Usage
-----
Forge mostly creates mock objects and function stubs, but in a variety of flavors. Using Forge always starts with creating a mock manager, called a Manager, which is created with the Forge class::

 from forge import Forge
 ...
 f = Forge()

There shouldn't be a real reason for keeping more than one forge manager. What it is typically used for is creating mocks::

 class SomeClass(object):
     def f(self, a, b, c):
         ...

 f = Forge()
 mock = f.create_mock(SomeClass)

Mock tests usually act in a record-replay manner. You record what you expect your mock to do, and then replay it, while Forge tracks what happens and makes sure it is correct::

 f.is_recording() # --> True
 mock.f(1, 2, 3)
 mock.f(3, 4, 5)

 f.replay()
 f.is_recording() # --> False
 f.is_replaying() # --> True
 mock.f(1, 2, 3)
 mock.f(3, 4, 5)

 f.verify() # this verifies no more calls are expected

To start over working from scratch, you can always perform::

 f.reset()

 
