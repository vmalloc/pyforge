class Sentinel(object):
    def __init__(self, __forge__name=None, **attrs):
        super(Sentinel, self).__init__()
        self.__forge__name = __forge__name
        for attr, value in attrs.iteritems():
            setattr(self, attr, value)
    def __repr__(self):
        name = self.__forge__name
        if name is None:
            name = "0x%x" % id(self)
        return "<Sentinel %s>" % name

