from .caller_info import CallerInfo

def _get_none_caller_info(level):
    return None

class ForgeDebug(object):
    def __init__(self, forge):
        super(ForgeDebug, self).__init__()
        self.disable()
    def disable(self):
        self._current_caller_info_getter = _get_none_caller_info
    def enable(self):
        self._current_caller_info_getter = CallerInfo.from_caller
    def get_caller_info(self, level=1):
        return self._current_caller_info_getter(level + 1)
