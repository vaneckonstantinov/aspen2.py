"""
This module provides helpers for testing applications that use Aspen.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
from collections import namedtuple

from . import resources
from .request_processor import RequestProcessor
from filesystem_tree import FilesystemTree


CWD = os.getcwd()


def teardown():
    """Standard teardown function.

    - reset the current working directory
    - remove FSFIX = %{tempdir}/fsfix
    - reset Aspen's global state
    - clear out sys.path_importer_cache

    """
    os.chdir(CWD)
    # Reset some process-global caches. Hrm ...
    resources.__cache__ = {}
    sys.path_importer_cache = {} # see test_weird.py

teardown() # start clean


class Harness(object):
    """A harness to be used in the Aspen test suite itself. Probably not useful to you.
    """

    def __init__(self):
        self.fs = namedtuple('fs', 'www project')
        self.fs.www = FilesystemTree()
        self.fs.project = FilesystemTree()
        self._request_processor = None

    def teardown(self):
        self.fs.www.remove()
        self.fs.project.remove()

    def hydrate_request_processor(self, **kwargs):
        if (self._request_processor is None) or kwargs:
            _kwargs = { 'www_root': self.fs.www.root
                      , 'project_root': self.fs.project.root
                       }
            _kwargs.update(kwargs)
            self._request_processor = RequestProcessor(**_kwargs)
        return self._request_processor

    request_processor = property(hydrate_request_processor)


    # Simple API
    # ==========

    def simple(self, contents='Greetings, program!', filepath='index.html.spt', uripath=None,
            querystring='', request_processor_configuration=None, **kw):
        """A helper to create a file and hit it through our machinery.
        """
        if filepath is not None:
            if isinstance(contents, tuple):
                contents, encoding = contents
            else:
                encoding = 'utf8'
            self.fs.www.mk((filepath, contents, True, encoding))
            if self._request_processor:
                # Rebuild the dispatch tree since we've just added a file
                self._request_processor.dispatcher.build_dispatch_tree()
        if request_processor_configuration is not None:
            self.hydrate_request_processor(**request_processor_configuration)

        if uripath is None:
            if filepath is None:
                uripath = '/'
            else:
                uripath = '/' + filepath
                if uripath.endswith('.spt'):
                    uripath = uripath[:-len('.spt')]
                for indexname in self.request_processor.indices:
                    if uripath.endswith(indexname):
                        uripath = uripath[:-len(indexname)]
                        break

        return self._hit('GET', uripath, querystring, **kw)

    def _hit(self, method, path='/', querystring='', raise_immediately=True, return_after=None,
             want='output', accept_header=None):

        state = self.request_processor.process( path
                                              , querystring
                                              , accept_header=accept_header
                                              , raise_immediately=raise_immediately
                                              , return_after=return_after
                                               )

        attr_path = want.split('.')
        base = attr_path[0]
        attr_path = attr_path[1:]

        try:
            out = state[base]
        except KeyError as e:
            raise KeyError(str(e) + '\nDebug info: state = ' + repr(state))
        try:
            for name in attr_path:
                out = getattr(out, name)
        except AttributeError as e:
            raise AttributeError(str(e) + '\nDebug info: out = ' + repr(out))

        return out

    def make_dispatch_result(self, *a, **kw):
        kw['return_after'] = 'dispatch_path_to_filesystem'
        kw['want'] = 'dispatch_result'
        return self.simple(*a, **kw)
