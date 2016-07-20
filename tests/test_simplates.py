# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from aspen.simplates.simplate import _decode
from pytest import raises


def test_default_media_type_works(harness):
    response = harness.simple("""
[---]
[---]
plaintext""", raise_immediately=False)
    assert "plaintext" in response.body

SIMPLATE="""
foo = %s
[---] via stdlib_format
{foo}"""

def test_can_use_path(harness):
    response = harness.simple( SIMPLATE % "path.raw"
                              )
    assert response.body == '/'


def test_cant_implicitly_override_state(harness):
    state = harness.simple("[---]\n"
        "resource = 'foo'\n"
        "[---] via stdlib_format\n"
        "{resource}",
        want='state'
    )
    assert state['output'].body == 'foo'
    assert state['resource'] != 'foo'


def test_can_explicitly_override_state(harness):
    state = harness.simple("# coding: utf8\n"
        "[---]\n"
        "class Output: body='thé'.encode('utf16'); media_type='text/x-foobar'; charset='utf16'\n"
        "state['output'] = Output()\n"
        "state['resource'] = 'foo'\n"
        "[---]\n",
        want='state'
    )
    output = state['output']
    assert output.body == 'thé'.encode('utf16')
    assert output.media_type == 'text/x-foobar'
    assert output.charset == 'utf16'
    assert state['resource'] == 'foo'


def test_but_python_sections_exhibit_module_scoping_behavior(harness):
    response = harness.simple("""[---]
bar = 'baz'
def foo():
    return bar
foo = foo()
[---] text/html via stdlib_format
{foo}""")
    assert response.body == 'baz'


def test_one_page_works(harness):
    response = harness.simple("Template")
    assert response.body == 'Template'


def test_two_pages_works(harness):
    response = harness.simple(SIMPLATE % "'Template'")
    assert response.body == 'Template'


def test_three_pages_one_python_works(harness):
    response = harness.simple("""
foo = 'Template'
[---] text/plain via stdlib_format
{foo}
[---] text/xml
<foo>{foo}</foo>""", filepath='index.spt')
    assert response.body.strip() == 'Template'


def test_three_pages_two_python_works(harness):
    response = harness.simple("""[---]
python_code = True
[---]
Template""")
    assert response.body == 'Template'


# _decode

def test_decode_can_take_encoding_from_first_line():
    actual = _decode(b"""\
    # -*- coding: utf8 -*-
    text = u'א'
    """)
    expected = """\
    # encoding set to utf8
    text = u'א'
    """
    assert actual == expected

def test_decode_can_take_encoding_from_second_line():
    actual = _decode(b"""\
    #!/blah/blah
    # -*- coding: utf8 -*-
    text = u'א'
    """)
    expected = """\
    #!/blah/blah
    # encoding set to utf8
    text = u'א'
    """
    assert actual == expected

def test_decode_prefers_first_line_to_second():
    actual = _decode(b"""\
    # -*- coding: utf8 -*-
    # -*- coding: ascii -*-
    text = u'א'
    """)
    expected = """\
    # encoding set to utf8
    # encoding NOT set to ascii
    text = u'א'
    """
    assert actual == expected

def test_decode_ignores_third_line():
    actual = _decode(b"""\
    # -*- coding: utf8 -*-
    # -*- coding: ascii -*-
    # -*- coding: cornnuts -*-
    text = u'א'
    """)
    expected = """\
    # encoding set to utf8
    # encoding NOT set to ascii
    # -*- coding: cornnuts -*-
    text = u'א'
    """
    assert actual == expected

def test_decode_can_take_encoding_from_various_line_formats():
    formats = [ b'-*- coding: utf8 -*-'
              , b'-*- encoding: utf8 -*-'
              , b'coding: utf8'
              , b'  coding: utf8'
              , b'\tencoding: utf8'
              , b'\t flubcoding=utf8'
               ]
    for fmt in formats:
        def test():
            actual = _decode(b"""\
            # {0}
            text = u'א'
            """.format(fmt))
            expected = """\
            # encoding set to utf8
            text = u'א'
            """
            assert actual == expected
        yield test

def test_decode_cant_take_encoding_from_bad_line_formats():
    formats = [ b'-*- coding : utf8 -*-'
              , b'foo = 0 -*- encoding: utf8 -*-'
              , b'  coding : utf8'
              , b'encoding : utf8'
              , b'  flubcoding =utf8'
              , b'coding: '
               ]
    for fmt in formats:
        def test():
            raw = b"""\
            # {0}
            text = u'א'
            """.format(fmt)
            raises(UnicodeDecodeError, _decode, raw)
        yield test
