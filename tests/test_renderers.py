from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pytest import raises

from aspen.simplates import json_
from aspen.simplates.renderers import Factory, Renderer


def test_a_custom_renderer(harness):
    class TestRenderer(Renderer):

        def compile(self, *a):
            return self.raw.upper()

        def render_content(self, context):
            d = dict((k, v) for k, v in self.__dict__.items() if k[0] != '_')
            return json_.dumps(d)

    class TestFactory(Factory):
        Renderer = TestRenderer

        def compile_meta(self, configuration):
            return 'foobar'

    request_processor = harness.request_processor
    request_processor.renderer_factories['lorem'] = TestFactory(request_processor)

    r = harness.simple("[---]\n[---] text/html via lorem\nLorem ipsum")
    d = json_.loads(r.body)
    assert d['meta'] == 'foobar'
    assert d['raw'] == 'Lorem ipsum'
    assert d['media_type'] == 'text/html'
    assert d['offset'] == 2
    assert d['compiled'] == 'LOREM IPSUM'


def test_renderer_padding_works_with_padded_output(harness):
    class TestRenderer(Renderer):

        def compile(self, filepath, padded):
            assert padded[:self.offset] == b'\n' * self.offset
            return padded

        def render_content(self, context):
            return b'\n' + self.compiled + b'\n'

    class TestFactory(Factory):
        Renderer = TestRenderer

    request_processor = harness.request_processor
    request_processor.renderer_factories['x'] = TestFactory(request_processor)

    output = harness.simple("[---]\n[---] text/plain via x\nSome text")
    assert output.body == '\nSome text\n'


def test_renderer_padding_works_with_stripped_output(harness):
    class TestRenderer(Renderer):

        def compile(self, filepath, padded):
            assert padded[:self.offset] == b'\n' * self.offset
            return padded

        def render_content(self, context):
            return b'\n' + self.raw + b'\n'

    class TestFactory(Factory):
        Renderer = TestRenderer

    request_processor = harness.request_processor
    request_processor.renderer_factories['y'] = TestFactory(request_processor)

    output = harness.simple("[---]\n[---] text/plain via y\nSome text")
    assert output.body == '\nSome text\n'


def test_renderer_padding_achieves_correct_line_numbers_in_tracebacks(harness):
    harness.fs.www.mk(('index.html.spt', '''\
    [---]
    [---] text/html via stdlib_template
    Greetings, $!
    '''))
    actual = str(raises(ValueError, harness._hit, 'GET', '/').value)
    assert 'line 3' in actual
