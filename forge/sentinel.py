class Sentinel(object):
    def __init__(self, __forge__name=None, **attrs):
        super(Sentinel, self).__init__()
        self.__forge__name = __forge__name
        for attr, value in attrs.iteritems():
            setattr(self, attr, value)
    def __repr__(self):
        return "<Sentinel %s>" % (self.__forge__name if self.__forge__name is not None else '?')

