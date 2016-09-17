import mimeparse

from ..exceptions import NegotiationFailure, NotFound
from ..output import Output


class Static(object):
    """Model a static HTTP resource.
    """

    def __init__(self, request_processor, fspath, raw, fs_media_type):
        assert type(raw) is bytes  # sanity check
        self.raw = raw
        self.fs_media_type = fs_media_type
        self.media_type = fs_media_type or request_processor.media_type_default
        self.charset = None
        if request_processor.charset_static:
            try:
                raw.decode(request_processor.charset_static)
                self.charset = request_processor.charset_static
            except UnicodeDecodeError:
                pass

    def render(self, context):
        return Output(body=self.raw, media_type=self.media_type, charset=self.charset)


class Dynamic(object):
    """Model a dynamic HTTP resource.
    """

    available_types = []  # populate in your subclass

    def render(self, state):
        """Render the resource with the given state as context, return Output.

        Before rendering we need to determine what type of content we're going
        to send back, by trying to find a match between the media types the
        client wants and the ones provided by the resource.

        The two sources for what the client wants are the extension in the
        request URL, and the Accept header. If the former fails to match we
        raise NotFound (404), if the latter fails we raise NegotiationFailure
        (406).

        Note that we don't always respect the `Accept` header (the spec says
        we can ignore it: <https://tools.ietf.org/html/rfc7231#section-5.3.2>).
        """
        available = self.available_types
        # When there is an extension in the URI path, the dispatcher gives us the
        # corresponding media type (or an empty string if unknown)
        accept = dispatch_accept = state['dispatch_result'].extra.get('accept')

        if accept is not None:
            # If the extension is unknown, raise NotFound
            if accept == '':
                raise NotFound()
            # Accept `media/type` for `media/x-type`
            i = accept.find('/x-')
            if i > 0:
                accept += ',' + accept[:i+1] + accept[i+3:]
            # Accept custom JSON media type
            if accept == 'application/json':
                accept += ',' + self.request_processor.media_type_json
        elif len(available) == 1:
            # If there's only one available type and no extension in the path,
            # then we ignore the Accept header
            return self.render_for_type(available[0], state)
        else:
            accept = state.get('accept_header')
        if accept:
            try:
                best_match = mimeparse.best_match(available, accept)
            except ValueError:
                # Unparseable accept header
                best_match = None
            if best_match:
                return self.render_for_type(best_match, state)
            elif best_match == '':
                if dispatch_accept is not None:
                    # e.g. client requested `/foo.json` but `/foo.spt` has no JSON page
                    raise NotFound()
                raise NegotiationFailure(accept, available)
        # Fall back to the first available type
        return self.render_for_type(available[0], state)
