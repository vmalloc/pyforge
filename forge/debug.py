import os
from .caller_info import CallerInfo

def _get_none_caller_info(level):
    return None

class ForgeDebug(object):
    def __init__(self, forge):
        super(ForgeDebug, self).__init__()
        if 'FORGE_DEBUG' in os.environ:
            self.enable()
        else:
            self.disable()
    def disable(self):
        self._enabled = False
        self._current_caller_info_getter = _get_none_caller_info
    def enable(self):
        self._enabled = True
        self._current_caller_info_getter = CallerInfo.from_caller
    def is_enabled(self):
        return self._enabled
    def get_caller_info(self, level=1):
        return self._current_caller_info_getter(level + 1)
