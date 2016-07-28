from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import re

import algorithm


# Register a 'repr' error strategy.
# =================================
# Before python 3.5 the 'backslashreplace' error handler only worked when
# encoding, not when decoding. The 'repr' handler below backports that
# bi-directionality to older python versions, including 2.7.

def replace_with_repr(unicode_error):
    offender = unicode_error.object[unicode_error.start:unicode_error.end]
    if isinstance(offender, bytes):
        r = ''.join(r'\x{0:x}'.format(b if isinstance(b, int) else ord(b))
                    for b in offender)
    else:
        r = offender.encode('ascii', 'backslashreplace').decode('ascii')
    return (r, unicode_error.end)

codecs.register_error('repr', replace_with_repr)


# Filters
# =======
# These are decorators for algorithm functions.

def by_lambda(filter_lambda):
    """
    """
    def wrap(function):
        def wrapped_function_by_lambda(*args,**kwargs):
            if filter_lambda():
                return function(*args,**kwargs)
        algorithm._transfer_func_name(wrapped_function_by_lambda, function)
        return wrapped_function_by_lambda
    return wrap


def by_regex(regex_tuples, default=True):
    """Only call function if

    regex_tuples is a list of (regex, filter?) where if the regex matches the
    requested URI, then the flow is applied or not based on if filter? is True
    or False.

    For example::

        from aspen.flows.filter import by_regex

        @by_regex( ( ("/secret/agenda", True), ( "/secret.*", False ) ) )
        def use_public_formatting(request):
            ...

    would call the 'use_public_formatting' flow step only on /secret/agenda
    and any other URLs not starting with /secret.

    """
    regex_res = [ (re.compile(regex), disposition) \
                           for regex, disposition in regex_tuples.items() ]
    def filter_function(function):
        def function_filter(request, *args):
            for regex, disposition in regex_res:
                if regex.matches(request.line.uri):
                    if disposition:
                        return function(*args)
            if default:
                return function(*args)
        algorithm._transfer_func_name(function_filter, function)
        return function_filter
    return filter_function


def by_dict(truthdict, default=True):
    """Filter for hooks

    truthdict is a mapping of URI -> filter? where if the requested URI is a
    key in the dict, then the hook is applied based on the filter? value.

    """
    def filter_function(function):
        def function_filter(request, *args):
            do_hook = truthdict.get(request.line.uri, default)
            if do_hook:
                return function(*args)
        algorithm._transfer_func_name(function_filter, function)
        return function_filter
    return filter_function
