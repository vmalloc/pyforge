from itertools import chain

from .queued_node import QueuedNodeParent


class QueuedGroup(QueuedNodeParent):
    def __init__(self, parent_group=None):
        super(QueuedGroup, self).__init__()
        self._parent_group = parent_group
        self._collection = []
        self._out_of_band_collection = []

    def is_empty(self):
        return not self.get_expected() and not self.get_available()

    def get_expected(self):
        return list(chain.from_iterable(obj.get_expected() for obj in self.iter_expected_or_available_children()))

    def get_available(self):
        return list(chain.from_iterable(obj.get_available() for obj in self.iter_expected_or_available_children()))

    def iter_expected_or_available_children(self):
        raise NotImplementedError()  # pragma: no cover

    def push(self, obj):
        self._collection.append(obj)
        obj.set_parent(self)
        return obj

    def push_out_of_band(self, obj):
        self._out_of_band_collection.append(obj)
        obj.set_parent(self)
        return obj

    def pop_matching(self, queued_object):
        result = self._pop_matching_by_strategy(queued_object)
        if result is None:
            result = self.pop_matching_out_of_band(queued_object)
        if result and self.get_parent() and not self.get_expected():
            self.get_parent().discard_child(self)
        return result

    def pop_matching_out_of_band(self, queued_object):
        for obj in self._out_of_band_collection:
            result = obj.pop_matching(queued_object)
            if result:
                return result
        return None

    def discard_child(self, queued_object):
        for collection in (self._collection, self._out_of_band_collection):
            for index, obj in enumerate(collection):
                if obj is queued_object:
                    collection.pop(index)
                    return

    def __len__(self):
        return sum(len(obj) for obj in chain(self._collection, self._out_of_band_collection))

    def __repr__(self):
        return "%s <id %s>(%s, out_of_band=%s)" % (type(self).__name__, id(self), repr(self._collection),
                                                   repr(self._out_of_band_collection))


class OrderedGroup(QueuedGroup):
    def iter_expected_or_available_children(self):
        return chain(self._collection[:1], self._out_of_band_collection)

    def _pop_matching_by_strategy(self, queued_object):
        return self._collection[0].pop_matching(queued_object) if self._collection else None


class AnyOrderGroup(QueuedGroup):
    def __init__(self, parent_group=None):
        super(AnyOrderGroup, self).__init__(parent_group)
        self._current_child = None

    def iter_expected_or_available_children(self):
        return chain(self._collection, self._out_of_band_collection)

    def discard_child(self, queued_object):
        returned = super(AnyOrderGroup, self).discard_child(queued_object)
        if queued_object is self._current_child:
            self._current_child = None
        return returned

    def _pop_matching_by_strategy(self, queued_object):
        if self._current_child:
            return self._current_child.pop_matching(queued_object)
        else:
            for obj in self._collection:
                # Save the current child so if it removes itself we won't set it as as the current child anymore.
                self._current_child = obj
                try:
                    result = obj.pop_matching(queued_object)
                except:
                    self._current_child = None
                    raise
                if result is not None:
                    return result
            self._current_child = None
        return None

    def __repr__(self):
        return "%s <id %s>(_current_child id=%s, %s, out_of_band=%s)" % (type(self).__name__, id(self),
                    id(self._current_child), repr(self._collection), repr(self._out_of_band_collection))


class InterleavedGroup(QueuedGroup):
    def iter_expected_or_available_children(self):
        return chain(self._collection, self._out_of_band_collection)

    def _pop_matching_by_strategy(self, queued_object):
        for obj in self._collection:
            result = obj.pop_matching(queued_object)
            if result is not None:
                return result
        return None

    def __repr__(self):
        return "%s <id %s>(%s, out_of_band=%s)" % (type(self).__name__, id(self), repr(self._collection),
                                                   repr(self._out_of_band_collection))
