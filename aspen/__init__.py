"""
#########
  Aspen
#########

Aspen is a filesystem dispatch library for Python web frameworks. Instead of
regular expressions, decorators, or object traversal, Aspen dispatches HTTP
requests based on the natural symmetry of URL paths and filesystem paths. In
the `immortal words`_ of Jeff Lindsay, "so like. a web server." Exactly! ;-)

.. _immortal words: https://twitter.com/progrium/status/773694289033383937

This is the documentation for the development version of the core Aspen
library, describing its filesystem dispatch behavior regardless of the web
framework you're using it with. For instructions on configuring Aspen with a
specific web framework, see the docs for `django-aspen`_, `Flask-Aspen`_, or
`Pando`_. See the `project homepage`_ for an overview.

.. _django-aspen: http://django.aspen.io/
.. _Flask-aspen: http://flask.aspen.io/
.. _Pando: http://pando.aspen.io/
.. _project homepage: http://aspen.io/

This version of Aspen has been tested with Python 2.7, 3.4, and 3.5, on both
Ubuntu and Windows.


**************
 Installation
**************

Aspen is available on `GitHub`_ and on `PyPI`_::

    $ pip install aspen

.. _GitHub: https://github.com/AspenWeb/aspen.py
.. _PyPI: https://pypi.python.org/pypi/aspen


*******
 Legal
*******

Aspen is distributed under the `MIT license`_.

.. _MIT license: https://github.com/AspenWeb/aspen.py/blob/master/COPYRIGHT


**********
 See Also
**********

The `Keystone`_ web framework was inspired by Aspen.

.. _Keystone: http://keystone.readthedocs.org/


**********
 Tutorial
**********

Foo bar


***********
 Reference
***********

No?

.. automodule:: aspen.simplates
.. automodule:: aspen.http
.. automodule:: aspen.request_processor
.. automodule:: aspen.resources
.. automodule:: aspen.output
.. automodule:: aspen.configuration
.. automodule:: aspen.exceptions
.. automodule:: aspen.testing
.. automodule:: aspen.utils

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

WINDOWS = sys.platform[:3] == 'win'
