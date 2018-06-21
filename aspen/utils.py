
class Constant(object):
    """A simple class that creates lightweight constants.

    >>> c = Constant('OK')
    >>> c
    OK
    >>> c.name
    'OK'
    >>> c == c
    True

    >>> c.name = 'KO'
    Traceback (most recent call last):
    ...
    AttributeError: constants cannot be modified

    >>> c2 = Constant('OK')
    >>> c2 == c
    False
    """

    __slots__ = 'name'

    def __init__(self, name):
        object.__setattr__(self, 'name', name)

    def __repr__(self):
        return self.name

    def __setattr__(self, name, value):
        raise AttributeError("constants cannot be modified")
