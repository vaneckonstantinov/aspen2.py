from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from ..utils import ascii_dammit


class ConfigurationError(StandardError):
    """This is an error in any part of our configuration.
    """

    def __init__(self, msg):
        StandardError.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


def configure(knobs, d, env_prefix, kwargs):
    for name, (default, func) in sorted(knobs.items()):

        # set the default value for this variable
        d[name] = default() if callable(default) else default

        def update(value, extend):
            if extend:
                d[name] += value
            else:
                d[name] = value

        # get from the environment
        envvar = env_prefix + name.upper()
        raw = os.environ.get(envvar, '').strip()
        if raw:
            update(*parse_conf_var(raw, func, 'environment', envvar))

        # get from kwargs
        raw = kwargs.get(name)
        if raw is not None:
            update(*parse_conf_var(raw, func, 'kwargs', name))


def parse_conf_var(raw, from_unicode, context, name_in_context):
    error = None
    value = raw
    if raw[0] == '+':
        value = raw[1:]
        extend = True
    else:
        value = raw
        extend = False
    try:
        if isinstance(value, str):
            value = value.decode('US-ASCII')
        return from_unicode(value), extend
    except UnicodeDecodeError as error:
        value = ascii_dammit(value)
        error_detail = "Configuration values must be US-ASCII."
    except ValueError as error:
        error_detail = error.args[0]

    msg = "Got a bad value '%s' for %s variable %s:"
    msg %= (value, context, name_in_context)
    if error_detail:
        msg += " " + error_detail + "."
    raise ConfigurationError(msg)
