from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pytest import raises

# Note: importing from `aspen.utils` installs the 'repr' error strategy
from aspen.utils import replace_with_repr

replace_with_repr  # shut up pyflakes

GARBAGE = b"a\xef\xf9"


def test_garbage_is_garbage():
    raises(UnicodeDecodeError, lambda s: s.decode('utf8'), GARBAGE)

def test_repr_error_strategy_works_when_decoding():
    errors = 'repr'
    actual = GARBAGE.decode('utf8', errors)
    assert actual == r"a\xef\xf9"

def test_repr_error_strategy_works_when_encoding():
    errors = 'repr'
    actual = 'comet: \u2604'.encode('ascii', errors)
    assert actual == br"comet: \u2604"
