class ForgeHandle(object):
    def __init__(self, forge):
        super(ForgeHandle, self).__init__()
        self.id = forge.get_new_handle_id()
        self.forge = forge
