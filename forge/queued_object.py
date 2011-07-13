class QueuedObject(object):
    def __init__(self, caller_info):
        super(QueuedObject, self).__init__()
        self.caller_info = caller_info
    def matches(self, queue_object):
        raise NotImplementedError()
    def describe(self):
        raise NotImplementedError()
    def __repr__(self):
        return "<%s>" % self.describe()
    def whenever(self):
        self.target.__forge__.forge.queue.allow_whenever(self)
        return self

