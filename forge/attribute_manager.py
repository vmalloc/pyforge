from collections import defaultdict
from sentinels import NOTHING

class AttributeManager(object):
    def __init__(self, forge):
        super(AttributeManager, self).__init__()
        self.forge = forge
        self._record_attributes = defaultdict(dict)
        self._replay_attributes = defaultdict(dict)
    def set_attribute(self, mock, attr, value):
        d = self._replay_attributes if self.forge.is_replaying() else self._record_attributes
        d[mock.__forge__.id][attr] = value
    def get_attribute(self, mock, attr):
        returned = self._get_attribute(mock, attr, self._replay_attributes)
        if returned is NOTHING:
            returned = self._get_attribute(mock, attr, self._record_attributes)
        return returned
    def _get_attribute(self, mock, attr, attr_dict):
        return attr_dict[mock.__forge__.id].get(attr, NOTHING)
    def reset_replay_attributes(self):
        self._replay_attributes.clear()
    def has_attribute(self, mock, attr):
        return attr in self._record_attributes[mock.__forge__.id] or attr in self._replay_attributes[mock.__forge__.id]
