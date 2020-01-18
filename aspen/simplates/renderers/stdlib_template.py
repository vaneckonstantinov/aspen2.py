from . import Renderer as BaseRenderer, Factory as BaseFactory
from string import Template


class Renderer(BaseRenderer):

    def compile(self, filepath, padded):
        return Template(padded)

    def render_content(self, context):
        return self.compiled.substitute(context)


class Factory(BaseFactory):
    Renderer = Renderer
