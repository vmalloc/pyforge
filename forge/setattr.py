from .queued_object import QueuedObject

class Setattr(QueuedObject):
    def __init__(self, target, name, value, caller_info):
        super(Setattr, self).__init__(caller_info)
        self.target = target
        self.name = name
        self.value = value
    def matches(self, other):
        if not isinstance(other, Setattr):
            return False
        return other.target is self.target and other.name == self.name and other.value == self.value
    def describe(self):
        return "setattr(%r, %r, %r)" % (self.target, self.name, self.value)
    
