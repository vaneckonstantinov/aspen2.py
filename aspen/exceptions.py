from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class ConfigurationError(Exception):
    """This is an error in any part of our configuration.
    """

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class LoadError(Exception):
    """Represent a problem loading a resource.
    """


class NegotiationFailure(Exception):

    def __init__(self, accept, available_types):
        self.accept = accept
        self.available_types = available_types
        message = "Couldn't satisfy %s. The following media types are available: %s."
        self.message = message % (self.accept, ', '.join(self.available_types))

    def __str__(self):
        return self.message


class TypecastError(Exception):

    def __init__(self, extension):
        self.msg = "Failure to typecast extension '{0}'".format(extension)
        Exception.__init__(self)
