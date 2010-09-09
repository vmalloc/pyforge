from collections import defaultdict

class MockMethodManager(object):
    def __init__(self, forge):
        super(MockMethodManager, self).__init__()
        self._initialized_method_stubs = defaultdict(dict)
        self._recorded_method_stubs = set()
    def get_initialized_method_stub_or_none(self, mock, method_name):
        return self._initialized_method_stubs[mock.__forge__.id].get(method_name, None)
    def add_initialized_method_stub(self, mock, method_name, method):
        self._initialized_method_stubs[mock.__forge__.id][method_name] = method
    def has_initialized_method_stub(self, mock, method_name):
        return self.get_initialized_method_stub_or_none(mock, method_name) is not None
