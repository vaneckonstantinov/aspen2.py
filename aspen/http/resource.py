import mimeparse
import mimetypes

from ..exceptions import NegotiationFailure, NotFound
from ..output import Output


class Static(object):
    """Model a static HTTP resource.
    """

    def __init__(self, request_processor, fspath, raw, fs_media_type):
        assert type(raw) is bytes  # sanity check
        self.fspath = fspath
        self.raw = raw if request_processor.store_static_files_in_ram else None
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
        output = Output(media_type=self.media_type, charset=self.charset)
        if self.raw is None:
            with open(self.fspath, 'rb') as f:
                output.body = f.read()
        else:
            output.body = self.raw
        return output


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

        dispatch_extension = state['dispatch_result'].extension
        if dispatch_extension:
            # There's an extension in the URI path, guess the media type from it
            dispatch_accept = mimetypes.guess_type('a.' + dispatch_extension, strict=False)[0]
            if dispatch_accept is None:
                # The extension is unknown, raise NotFound
                raise NotFound()
            accept = dispatch_accept
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
            dispatch_accept = None
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
