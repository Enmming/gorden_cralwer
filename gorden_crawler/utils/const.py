import sys

class Const(object):
    class ConstError(object): pass
    def __setattr__(self, key, value):
        if self.__dict__.has_key(key):
            raise self.ConstError, "Changing const.%s" % key
        else:
            self.__dict__[key] = value
    def __getattr__(self, key):
        if self.__dict__.has_key(key):
            return self.key
        else:
            return None

sys.modules[__name__] = Const()