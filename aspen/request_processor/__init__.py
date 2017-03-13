"""
################################
 :mod:`aspen.request_processor`
################################

The request processor dispatches requests to the filesystem (typecasting URL
path variables), loads the resource from the filesystem, and then renders and
encodes the resource.

.. contents::
    :local:

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import errno
import mimetypes
import os
import sys
from collections import defaultdict

from algorithm import Algorithm

from .typecasting import defaults as default_typecasters
from ..http.resource import Static
from ..configuration import ConfigurationError, configure, parse


default_indices = lambda: ['index.html', 'index.json', 'index',
                           'index.html.spt', 'index.json.spt', 'index.spt']


    # 'name':               (default,               from_unicode)
KNOBS = \
    { 'changes_reload':     (False,                 parse.yes_no)
    , 'charset_static':     (None,                  parse.codec)
    , 'encode_output_as':   ('UTF-8',               parse.codec)
    , 'indices':            (default_indices,       parse.list_)
    , 'media_type_default': ('text/plain',          parse.media_type)
    , 'media_type_json':    ('application/json',    parse.media_type)
    , 'project_root':       (None,                  parse.identity)
    , 'renderer_default':   ('stdlib_percent',      parse.renderer)
    , 'www_root':           (None,                  parse.identity)
     }


class RequestProcessor(object):
    """Define a parasitic request processor.

    It depends on a host framework for real request/response objects.

    """

    def __init__(self, **kwargs):
        """Takes configuration in kwargs.

        See the `KNOBS` global variable for valid keys and default values.
        """
        self.algorithm = Algorithm.from_dotted_name('aspen.request_processor.algorithm')
        self.configure(**kwargs)


    def process(self, path, querystring, accept_header, raise_immediately=None, return_after=None,
                **kw):
        """Given a path, querystring, and Accept header, return a state dict.
        """
        return self.algorithm.run( request_processor=self
                                 , path=path
                                 , querystring=querystring
                                 , accept_header=accept_header
                                 , _raise_immediately=raise_immediately
                                 , _return_after=return_after
                                 , **kw
                                  )

    def configure(self, **kwargs):
        """Takes a dictionary of strings/unicodes to strings/unicodes.
        """

        # Do some base-line configuration.
        # ================================
        # We want to do the following configuration of our Python environment
        # regardless of the user's configuration preferences

        # mimetypes
        aspens_mimetypes = os.path.join(os.path.dirname(__file__), 'mime.types')
        mimetypes.knownfiles += [aspens_mimetypes]
        # mimetypes.init is called below after the user has a turn.

        # XXX register codecs here

        self.typecasters = default_typecasters


        # Configure from defaults and kwargs.
        # ===================================

        configure(KNOBS, self.__dict__, None, kwargs)


        # Set some attributes.
        # ====================

        def safe_getcwd(errorstr):
            try:
                # If the working directory no longer exists, then the following
                # will raise OSError: [Errno 2] No such file or directory. I
                # swear I've seen this under supervisor, though I don't have
                # steps to reproduce. :-(  To get around this you specify a
                # www_root explicitly, or you can use supervisor's cwd
                # facility.

                return os.getcwd()
            except OSError as err:
                if err.errno != errno.ENOENT:
                    raise
                raise ConfigurationError(errorstr)

        # project root
        if self.project_root is not None:
            # canonicalize it
            if not os.path.isabs(self.project_root):
                cwd = safe_getcwd(
                    "Could not get a current working directory. You can specify "
                    "project_root in kwargs."
                )
                self.project_root = os.path.join(cwd, self.project_root)

            self.project_root = os.path.realpath(self.project_root)

            # mime.types
            users_mimetypes = os.path.join(self.project_root, 'mime.types')
            mimetypes.knownfiles += [users_mimetypes]

            # PYTHONPATH
            sys.path.insert(0, self.project_root)

        # www_root
        if self.www_root is None:
            self.www_root = safe_getcwd(
                "Could not get a current working directory. You can specify "
                "www_root in kwargs."
            )

        self.www_root = os.path.realpath(self.www_root)

        # kludge simplates -- should move out into a simplate plugin
        from ..simplates.renderers import factories
        from ..simplates.simplate import Simplate, SimplateDefaults
        Simplate.renderer_factories = factories(self)
        Simplate.default_renderers_by_media_type = defaultdict(lambda: self.renderer_default)
        Simplate.default_renderers_by_media_type[self.media_type_json] = 'json_dump'

        initial_context = { 'request_processor': self }
        Simplate.defaults = SimplateDefaults(
            Simplate.default_renderers_by_media_type,
            Simplate.renderer_factories,
            initial_context
        )

        # set up dynamic class mapping
        self.dynamic_classes_by_file_extension = dict(spt=Simplate)

        # mime.types
        # ==========
        # It turns out that init'ing mimetypes is somewhat expensive. This is
        # significant in testing, though in dev/production you wouldn't notice.
        # In any case this means that if a devuser inits mimetypes themselves
        # then we won't do so again here, which is fine. Right?

        if not mimetypes.inited:
            mimetypes.init()


    def is_dynamic(self, fspath):
        """Given a filesystem path, return a boolean.
        """
        return self.get_resource_class(fspath) is not Static


    def get_resource_class(self, fspath):
        """Given a filesystem path, return a resource class.
        """
        parts = fspath.split('.')
        extension = parts[-1] if len(parts) > 1 else None
        return self.dynamic_classes_by_file_extension.get(extension, Static)
