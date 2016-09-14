"""
:mod:`output`
=============

Implement a class for capturing request processing output.

"""

class Output(object):
    body = media_type = charset = None

    def __init__(self, **kw):
        self.__dict__.update(kw)

    @property
    def text(self):
        return self.body.decode(self.charset) if self.charset else None
