"""
####################
 :mod:`aspen.utils`
####################

This module collects a few random bits that should be placed somewhere that
makes more sense.

.. contents::
    :local:

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs


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
