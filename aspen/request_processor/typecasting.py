"""
This module handles the parsing of path variables.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..exceptions import TypecastError


#: Aspen's default typecasters.
defaults = { 'int': lambda pathpart, state: int(pathpart)
           , 'float': lambda pathpart, state: float(pathpart)
            }


def apply_typecasters(typecasters, path_vars, state):
    """Perform typecasting (in-place!).

    :arg typecasters: a :class:`dict` of type names to typecast functions
    :arg path_vars: a :class:`~aspen.http.mapping.Mapping` of path variables
    :arg state: a :class:`dict` passed to typecast functions as second argument
    :raises TypecastError: if a typecast function raises an exception
    """
    for part in list(path_vars.keys()):
        pieces = part.rsplit('.',1)
        if len(pieces) > 1:
            var, ext = pieces
            if ext in typecasters:
                try:
                    # path_vars is a Mapping not a dict, so:
                    for v in path_vars.all(part):
                        path_vars.add(var, typecasters[ext](v, state))
                    path_vars.popall(part)
                except:
                    raise TypecastError(ext)

