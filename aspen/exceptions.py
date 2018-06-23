"""
This module defines all of the custom exceptions used across the Aspen library.
"""
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


class NegotiationFailure(Exception):
    """The requested media type isn't available (HTTP status code 406).
    """

    def __init__(self, accept, available_types):
        self.accept = accept
        self.available_types = available_types
        message = "Couldn't satisfy %s. The following media types are available: %s."
        self.message = message % (self.accept, ', '.join(self.available_types))

    def __str__(self):
        return self.message


class TypecastError(Exception):
    """Parsing a segment of the request path failed (HTTP status code 404).
    """

    def __init__(self, extension):
        self.msg = "Failure to typecast extension '{0}'".format(extension)
        Exception.__init__(self)


class NotFound(Exception):
    """The requested resource isn't available (HTTP status code 404).
    """

    def __init__(self, message=''):
        self.message = message or "not found"


class SlugCollision(Exception):
    """Raised if two files claim the same URL path.

    Example: ``foo.html`` and ``foo.html.spt`` both claim ``/foo.html``.
    """

class WildcardCollision(Exception):
    """Raised if a filesystem path contains multiple wildcards with the same name.

    Examples: ``www/%foo/%foo/index.spt``, ``www/%foo/bar/%foo.spt``.
    """
