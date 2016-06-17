from ..output import Output
from ..request_processor import dispatcher
from ..simplates.simplate import Simplate, SimplateDefaults, SimplateException


class Static(object):
    """Model a static HTTP resource.
    """

    def __init__(self, request_processor, fspath, raw, media_type):
        self.request_processor = request_processor
        self.raw = raw
        self.media_type = media_type
        if media_type == 'application/json':
            self.media_type = self.request_processor.media_type_json

    def render(self, context):
        output = Output()
        # XXX Perform HTTP caching here.
        assert type(self.raw) is str # sanity check
        output.body = self.raw
        output.media_type = self.media_type
        if self.media_type.startswith('text/'):
            output.charset = self.request_processor.charset_static
        return output


class Dynamic(Simplate):
    """Model a dynamic HTTP resource using simplates.

       Most defaults are in request_processor, so make SimplateDefaults from that.

       Make .request_processor available as it has been historically.

       Figure out which accept header to use.

       Append a charset to text Content-Types if one is known.


    """

    def __init__(self, request_processor, fs, raw, default_media_type):
        self.request_processor = request_processor
        initial_context = { 'request_processor': request_processor }
        defaults = SimplateDefaults(request_processor.default_renderers_by_media_type,
                                    request_processor.renderer_factories,
                                    initial_context)
        super(Dynamic, self).__init__(defaults, fs, raw, default_media_type)


    def render(self, state):
        accept = dispatch_accept = state['dispatch_result'].extra.get('accept')
        if accept is None:
            accept = state.get('accept_header')
        try:
            return super(Dynamic, self).render(accept, state)
        except SimplateException as e:
            # find an Accept header
            if dispatch_accept is not None:  # indirect negotiation
                raise dispatcher.IndirectNegotiationFailure()
            else:                            # direct negotiation
                message = "Couldn't satisfy %s. The following media types are available: %s."
                message %= (accept, ', '.join(e.available_types))
                raise dispatcher.DirectNegotiationFailure(message.encode('US-ASCII'))
