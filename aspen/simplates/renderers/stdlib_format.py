from . import Renderer, Factory


class Renderer(Renderer):

    def render_content(self, context):
        return self.compiled.format(**context)


class Factory(Factory):
    Renderer = Renderer
