class ForgeHandle(object):
    def __init__(self, forge):
        super(ForgeHandle, self).__init__()
        self.id = forge.get_new_handle_id()
        self.forge = forge
        self._forced_description = None
    def describe(self):
        if self._forced_description is not None:
            return self._forced_description
        return self._describe()
    def _describe(self):
        raise NotImplementedError()
    def set_description(self, d):
        self._forced_description = d
