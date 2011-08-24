import re
from .python3_compat import basestring

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
            return self._class is type(other)
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

class Contains(Comparator):
    def __init__(self, *objs):
        super(Contains, self).__init__()
        self._objs = objs
    def equals(self, other):
        try:
            return all(obj in other for obj in self._objs)
        except TypeError:
            return False

class HasKeyValue(Comparator):
    def __init__(self, key, value):
        super(HasKeyValue, self).__init__()
        self._key = key
        self._value = value
    def equals(self, other):
        try:
            return other[self._key] == self._value
        except TypeError:
            return False
        except KeyError:
            return False

class HasAttributeValue(Comparator):
    def __init__(self, attr, value):
        super(HasAttributeValue, self).__init__()
        self._attr = attr
        self._value = value
    def equals(self, other):
        try:
            return getattr(other, self._attr) == self._value
        except TypeError:
            return False
        except AttributeError:
            return False

class Anything(Comparator):
    def equals(self, other):
        return True

class And(Comparator):
    def __init__(self, *comparators):
        super(And, self).__init__()
        if not comparators:
            raise TypeError("At least one comparator must be specified for And()")
        self.comparators = comparators
    def equals(self, other):
        return all(c.equals(other) for c in self.comparators)

StrContains = lambda *xs: And(IsA(basestring), Contains(*xs))

class Or(Comparator):
    def __init__(self, *comparators):
        super(Or, self).__init__()
        if not comparators:
            raise TypeError("At least one comparator must be specified for Or()")
        self.comparators = comparators
    def equals(self, other):
        return any(c.equals(other) for c in self.comparators)
class Not(Comparator):
    def __init__(self, comparator):
        super(Not, self).__init__()
        self.comparator = comparator
    def equals(self, other):
        return not self.comparator.equals(other)
