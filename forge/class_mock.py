from .class_mock_handle import ClassMockHandle
from .mock_object import MockObject

class ClassMockObject(MockObject):
    def __init__(self, forge, mocked_class, behave_as_instance, hybrid):
        super(ClassMockObject, self).__init__()
        self.__forge__ = ClassMockHandle(forge, self, mocked_class, behave_as_instance, hybrid)
    def __getattribute__(self, name):
        if name == '__class__':
            if self.__forge__.behaves_as_instance:
                return self.__forge__.mocked_class
            return type(self.__forge__.mocked_class)
        else:
            return super(ClassMockObject, self).__getattribute__(name)
