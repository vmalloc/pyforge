from .queued_node import QueuedNode


class QueuedObject(QueuedNode):
    """Base object for all leafs in the call tree."""
    def __init__(self, caller_info):
        super(QueuedObject, self).__init__()
        self.caller_info = caller_info

    def matches(self, queue_object):
        """Returns True if the object matches queue_object. Implemented by derived classes."""
        raise NotImplementedError()  # pragma: no cover

    def describe(self):
        raise NotImplementedError()  # pragma: no cover

    def __repr__(self):
        return "<%s>" % self.describe()

    def __len__(self):
        return 1

    def pop_matching(self, queue_object):
        if not self.matches(queue_object):
            return None

        if self.get_parent():
            self.get_parent().discard_child(self)

        return self
