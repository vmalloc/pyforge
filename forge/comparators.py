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
