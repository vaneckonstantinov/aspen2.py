from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import copy
import os

from ..exceptions import ConfigurationError


MISSING = object()


def configure(knobs, d, env_prefix, kwargs):
    for name, (default, func) in sorted(knobs.items()):

        # set the default value for this variable
        d[name] = default() if callable(default) else default

        # get from kwargs
        raw = kwargs.get(name, MISSING)
        if raw is not MISSING:
            d[name] = parse_conf_var(raw, func, name)


def parse_conf_var(raw, from_unicode, name):
    value = raw
    try:
        if isinstance(value, bytes):
            value = value.decode('US-ASCII')
        return from_unicode(value)
    except UnicodeDecodeError as error:
        value = value.decode('US-ASCII', 'backslashreplace')
        error_detail = "Configuration values must be US-ASCII"
    except ValueError as error:
        error_detail = error.args[0]

    msg = "Got a bad value '%s' for variable %s: %s."
    raise ConfigurationError(msg % (value, name, error_detail))
