from collections import defaultdict

class AttributeManager(object):
    def __init__(self, forge):
        super(AttributeManager, self).__init__()
        self._attributes = defaultdict(dict)
    def set_attribute(self, mock, attr, value):
        self._attributes[mock.__forge__.id][attr] = value
    def get_attribute(self, mock, attr):
        return self._attributes[mock.__forge__.id][attr]
    def has_attribute(self, mock, attr):
        return attr in self._attributes[mock.__forge__.id]
