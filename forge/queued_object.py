class QueuedObject(object):
    def matches(self, queue_object):
        raise NotImplementedError()
    def describe(self):
        raise NotImplementedError()
