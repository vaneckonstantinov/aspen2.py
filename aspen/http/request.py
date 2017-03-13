from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import PY2, text_type as str
from six.moves.urllib.parse import parse_qs, unquote, unquote_plus

from .mapping import Mapping


def _decode(o, errors='strict'):
    return o.decode('utf8', errors=errors) if isinstance(o, bytes) else o


def path_decode(bs):
    return _decode(unquote(bs.encode('ascii') if PY2 else bs))


class PathPart(str):
    """A string with a mapping for extra data about it."""

    __slots__ = ['params']

    def __new__(cls, value, params=None):
        obj = super(PathPart, cls).__new__(cls, value)
        obj.params = params
        return obj


def extract_rfc2396_params(path):
    """RFC2396 section 3.3 says that path components of a URI can have
    'a sequence of parameters, indicated by the semicolon ";" character.'
    and that ' Within a path segment, the characters "/", ";", "=", and
    "?" are reserved.'  This way you can do
    /frisbee;color=red;size=small/logo;sponsor=w3c;color=black/image.jpg
    and each path segment gets its own params.

    https://tools.ietf.org/html/rfc3986#section-3.3

    * path should be raw so we don't split or operate on a decoded character
    * output is decoded
    """
    pathsegs = path.lstrip('/').split('/')
    segments_with_params = []
    for component in pathsegs:
        parts = component.split(';')
        params = Mapping()
        segment = path_decode(parts[0])
        for p in parts[1:]:
            if '=' in p:
                k, v = p.split('=', 1)
            else:
                k, v = p, ''
            params.add(path_decode(k), path_decode(v))
        segments_with_params.append(PathPart(segment, params))
    return segments_with_params


def split_path_no_params(path):
    """This splits a path into parts on "/" only (no split on ";" or ",").
    """
    return [PathPart(path_decode(s)) for s in path.lstrip('/').split('/')]


class Path(Mapping):
    """Represent the path of a resource.
    """

    def __init__(self, raw, split_path=extract_rfc2396_params):
        self.raw = raw
        self.decoded = path_decode(raw)
        self.parts = split_path(raw)


class Querystring(Mapping):
    """Represent an HTTP querystring.
    """

    def __init__(self, raw, errors='replace'):
        """Takes a string of type application/x-www-form-urlencoded.
        """
        # urllib needs bytestrings in py2 and unicode strings in py3
        raw_str = raw.encode('ascii') if PY2 else raw

        self.decoded = _decode(unquote_plus(raw_str), errors=errors)
        self.raw = raw

        common_kw = dict(keep_blank_values=True, strict_parsing=False)
        if PY2:
            # in python 2 parse_qs does its own unquote_plus'ing ...
            as_dict = parse_qs(raw_str, **common_kw)
            # ... but doesn't decode to unicode.
            for k, vals in list(as_dict.items()):
                as_dict[_decode(k, errors=errors)] = [
                    _decode(v, errors=errors) for v in vals
                ]
        else:
            # in python 3 parse_qs does the decoding
            as_dict = parse_qs(raw_str, errors=errors, **common_kw)

        Mapping.__init__(self, as_dict)
