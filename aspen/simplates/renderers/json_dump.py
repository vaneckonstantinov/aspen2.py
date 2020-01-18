from . import Renderer as BaseRenderer, Factory as BaseFactory
from .. import json_


class Renderer(BaseRenderer):

    def render_content(self, context):
        output = context['output']
        if not output.media_type:
            output.media_type = context['request_processor'].media_type_json
        r = json_.dumps(eval(self.compiled, globals(), context))
        if isinstance(r, bytes):
            r = r.decode('ascii')
        return r


class Factory(BaseFactory):
    Renderer = Renderer
