import sys

class CallerInfo(object):
    def __init__(self, file_name, line_number, function_name):
        super(CallerInfo, self).__init__()
        self.file_name = file_name
        self.line_number = line_number
        self.function_name = function_name
    def __repr__(self):
        return "%s:%s::%s" % (self.file_name, self.line_number, self.function_name)
    @classmethod
    def from_caller(cls, level=1, _frame_getter=sys._getframe):
        """
        @param level: how many calls above this one is to
            be retrieved (1 is the caller to this function)
        """
        frame = _frame_getter(level + 1)
        try:
            returned = cls(file_name=frame.f_code.co_filename,
                           line_number=frame.f_lineno,
                           function_name=frame.f_code.co_name)
        finally:
            #necessary to prevent memory leaks, just in case __del__
            #pops up some day
            del frame
        return returned
