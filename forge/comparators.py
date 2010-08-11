import re

class Comparator(object):
    def equals(self, other):
        raise NotImplementedError()
    def __eq__(self, other):
        return self.equals(other)
    def __ne__(self, other):
        return not (self == other)
    def __repr__(self):
        return "<Comparator %s>" % (type(self).__name__)

class Is(Comparator):
    def __init__(self, obj):
        super(Is, self).__init__()
        self._obj = obj
    def equals(self, other):
        return self._obj is other
    def __repr__(self):
        return "<Is %r (id=0x%x)>" % (self._obj, id(self._obj))

class IsA(Comparator):
    def __init__(self, klass):
        super(IsA, self).__init__()
        self._class = klass
    def equals(self, other):
        try:
            return isinstance(other, self._class)
        except TypeError:
            return type(self._class) is type(other)
    def __repr__(self):
        return "<Is instance of %r >" % (self._class,)

class RegexpMatches(Comparator):
    def __init__(self, regexp, flags=0):
        super(RegexpMatches, self).__init__()
        self._regexp = regexp
        self._flags = flags
    def equals(self, other):
        if not isinstance(other, basestring):
            return False
        return re.match(self._regexp, other, self._flags)
    def __repr__(self):
        return "<Matches %r>" % (self._regexp,)

class Func(Comparator):
    def __init__(self, func):
        super(Func, self).__init__()
        self._func = func
    def equals(self, other):
        return self._func(other)
    def __repr__(self):
        return "<Function predicate %s>" % (self._func,)

class IsAlmost(Comparator):
    def __init__(self, value, places=7):
        super(IsAlmost, self).__init__()
        self._value = value
        self._places = places
    def equals(self, other):
        try:
            return round(self._value - other, self._places) == 0
        except TypeError:
            return False
