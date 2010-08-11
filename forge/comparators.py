import re

class Comparator(object):
    def equals(self, other):
        raise NotImplementedError()
    def __eq__(self, other):
        return self.equals(other)
    def __ne__(self, other):
        return not (self == other)

class Is(Comparator):
    def __init__(self, obj):
        super(Is, self).__init__()
        self._obj = obj
    def equals(self, other):
        return self._obj is other

class IsA(Comparator):
    def __init__(self, klass):
        super(IsA, self).__init__()
        self._class = klass
    def equals(self, other):
        try:
            return isinstance(other, self._class)
        except TypeError:
            return type(self._class) is type(other)

class RegexpMatches(Comparator):
    def __init__(self, regexp, flags=0):
        super(RegexpMatches, self).__init__()
        self._regexp = regexp
        self._flags = flags
    def equals(self, other):
        if not isinstance(other, basestring):
            return False
        return re.match(self._regexp, other, self._flags)
