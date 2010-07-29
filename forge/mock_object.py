from mock_handle import MockHandle

class MockObject(object):
    def __init__(self, forge):
        super(MockObject, self).__init__()
        self.__forge__ = MockHandle(forge, self)
