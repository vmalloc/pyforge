class Sentinel(object):
    def __init__(self, name=None):
        super(Sentinel, self).__init__()
        self.name = name
    def __repr__(self):
        return "<Sentinel %s>" % (self.name if self.name is not None else '?')

