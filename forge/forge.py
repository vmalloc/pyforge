class Forge(object):
    def __init__(self):
        super(Forge, self).__init__()
        self._is_replaying = False
    def isReplaying(self):
        return self._is_replaying
    def reset(self):
        self._is_replaying = False
    def replay(self):
        self._is_replaying = True
