class QueuedNode(object):
    """Base class for all nodes in the call tree. A node may be an actual call or attribute set/get, in this case this
    is a leaf node, or a call group (ordered, unordered, etc.), in that case it's a branch node."""

    def __init__(self):
        super(QueuedNode, self).__init__()
        self._parent = None

    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def get_expected(self):
        return [self]

    def get_available(self):
        return [self]

    def pop_matching(self, queue_object):
        """Provide the node with the opportunity to remove queue_object from its subtree. Usually called after
        a call to matches(queue_object) as been made.
        Returns the matching queued object or None if not found."""
        raise NotImplementedError()  # pragma: no cover


class QueuedNodeParent(QueuedNode):
    """Base class for all non-leaf nodes."""
    def discard_child(self, child):
        raise NotImplementedError()  # pragma: no cover
