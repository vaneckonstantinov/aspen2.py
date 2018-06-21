from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import typecasting
from .dispatcher import DispatchStatus
from .. import resources
from ..http.request import Path, Querystring


def hydrate_path(path):
    return {'path': Path(path)}


def hydrate_querystring(querystring):
    return {'querystring': Querystring(querystring)}


def dispatch_path_to_filesystem(request_processor, path):
    result = request_processor.dispatcher.dispatch(path.decoded, path.parts)
    if result.wildcards:
        for k, v in result.wildcards.items():
            path[k] = v
    return {'dispatch_result': result}


def apply_typecasters_to_path(request_processor, path, state):
    typecasting.apply_typecasters( request_processor.typecasters
                                 , path
                                 , state
                                  )


def load_resource_from_filesystem(request_processor, dispatch_result):
    if dispatch_result.match and dispatch_result.status == DispatchStatus.okay:
        return {'resource': resources.get(request_processor, dispatch_result.match)}


def render_resource(state, resource=None):
    if resource:
        return {'output': resource.render(state)}


def encode_output(request_processor, output=None):
    if output and not isinstance(output.body, bytes):
        output.charset = request_processor.encode_output_as
        output.body = output.body.encode(output.charset)
