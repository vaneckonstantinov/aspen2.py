from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs

from ..simplates.renderers import RENDERERS


def identity(value):
    return value

def media_type(media_type):
    # XXX for now. Read a spec
    return media_type.encode('ascii').decode('ascii')

def codec(value):
    codecs.lookup(value)
    return value

def yes_no(s):
    s = s.lower()
    if s in ['yes', 'true', '1']:
        return True
    if s in ['no', 'false', '0']:
        return False
    raise ValueError("must be either yes/true/1 or no/false/0")

def list_(value):
    # populate out with a single copy of each non-empty item, preserving order
    out = []
    for v in value.split(','):
        v = v.strip()
        if v and not v in out:
            out.append(v)
    return out

def renderer(value):
    if value not in RENDERERS:
        msg = "not one of {%s}" % (','.join(RENDERERS))
        raise ValueError(msg)
    return value
