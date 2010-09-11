from class_mock_handle import ClassMockHandle
from mock_object import MockObject

class ClassMockObject(MockObject):
    def __init__(self, forge, mocked_class, behave_as_instance, hybrid):
        super(ClassMockObject, self).__init__()
        self.__forge__ = ClassMockHandle(forge, self, mocked_class, behave_as_instance, hybrid)
    @property
    def __class__(self):
        if self.__forge__.behaves_as_instance:
            return self.__forge__.mocked_class
        return type(self.__forge__.mocked_class)
