#######################
 How to Write a Plugin
#######################

This document is for people who want to write a plugin for Aspen. If you only
want to use Aspen with existing plugins, then ... what?

Negotiated and rendered resources have content pages the bytes for which are
transformed based on context. The user may explicitly choose a renderer per
content page, with the default renderer per page computed from its media type.
Template resources derive their media type from the file extension. Negotiated
resources have no file extension by definition, so they specify the media type
of their content pages in the resource itself, on the so-called "specline" of
each content page, like so::

    [---]
    [---] text/plain
    Greetings, program!
    [---] text/html
    <h1>Greetings, program!</h1>


A Renderer is instantiated by a Factory, which is a class that is itself
instantied with one argument::

    configuration   an Aspen configuration object


Instances of each Renderer subclass are callables that take five arguments and
return a function (confused yet?). The five arguments are::

    factory         the Factory creating this object
    filepath        the filesystem path of the resource in question
    raw             the bytestring of the page of the resource in question
    media_type      the media type of the page
    offset          the line number at which the page starts


Each Renderer instance is a callable that takes a context dictionary and
returns a bytestring of rendered content. The heavy lifting is done in the
render_content method.

Here's how to implement and register your own renderer::

    from aspen.simplates.renderers import Renderer, Factory

    class Cheese(Renderer):
        def render_content(self, context):
            return self.raw.replace("cheese", "CHEESE!!!!!!")

    class CheeseFactory(Factory):
        Renderer = Cheese

    request_processor.renderer_factories['excited-about-cheese'] = CheeseFactory(request_processor)


Put that in your startup script. Now you can use it in a negotiated or rendered
resource::

    [---] via excited-about-cheese
    I like cheese!


Out will come::

    I like CHEESE!!!!!!!


If you write a new renderer for inclusion in the base Aspen distribution,
please work with Aspen's existing reloading machinery, etc. as much as
possible. Use the existing template shims as guidelines, and if Aspen's
machinery is inadequate for some reason let's evolve the machinery so all
renderers behave consistently for users. Thanks.
