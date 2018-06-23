#########################
 How to Write a Simplate
#########################

Aspen dispatches web requests to files on the filesystem based on paths, but
what kind of files does it expect to find there? The answer is simplates.
Simplates are a file format combining request processing logic---like you'd
find in a `Django view`_ or a `Rails controller`_---with template code, in one
file with multiple sections.

.. _Django view: https://docs.djangoproject.com/en/1.10/topics/http/views/
.. _Rails controller: http://guides.rubyonrails.org/action_controller_overview.html


.. note::

    Check the Aspen homepage for links to `simplate support for your favorite
    text editor`_.

    .. _simplate support for your favorite text editor: http://aspen.io/


------------------------
 Sections of a Simplate
------------------------

What are the sections of a simplate? Let's illustrate by example::

    import random

    [----------------------------------]
    program = querystring['program']
    excitement = '!' * random.randint(1, 10)

    [----] text/html via stdlib_template
    <h1>Greetings, $program$excitement</h1>

    [-----] text/plain via stdlib_format
    Greetings, {program}{excitement}

    [---] application/json via json_dump
    {"program": program, "excitement": excitement}

The first thing to notice is that the file is separated into multiple sections
using lines that begin with the characters ``[---]``. There must be at least
three dashes, but more are fine.

Sections in a simplate are either "logic sections" or "content sections".
Content sections may have a "specline" after the ``[---]`` separator. The
format of the specline is ``content-type via renderer``. The syntax of the
content sections depends on the renderer. The logic sections are Python.

.. note::

    Simplates under Python 2.7 use the following :mod:`__future__` features:
    :mod:`absolute_import`, :mod:`division`, :mod:`print_function`, and
    :mod:`unicode_literals`.

A simplate may have one or more sections. Here are the rules for determining
which section is what:

1. **If a simplate only has one section**, it's a content section.

#. **If a simplate has two sections**, the first is *request* logic (runs for 
   every request), and the second is a content section.

#. **If a simplate has more than two sections**:

  a. If the second section has a specline, then the first is request logic, and
     the rest are content sections.

  #. If the second section has no specline, then the first is *initialization*
     logic (runs once when the page is first hit), the second is request
     logic, and the rest are content sections.


Putting that all together, we see that the above example has five sections:

#. a logic section containing Python that will run once when the page is first hit,
#. a request section containing Python that will run every time the page is hit,
#. a section for rendering ``text/html`` via Python templates,
#. a section for rendering ``text/plain`` via new-style Python string formatting, and
#. a section for rendering ``application/json`` via Python's :mod:`json` library.


---------
 Context
---------

The power of simplates is that objects you define in the logic sections are
automatically available to the templates in your content sections. The above
example illustrates this with the ``program`` and ``excitement`` variables.
Moreover, Aspen makes various objects available to the logic sections of your
simplates (besides the Python builtins).

Here's what you get:

- ``path``---a representation of the URL path
- ``querystring``---a representation of the URL querystring
- ``request_processor``---a :mod:`~aspen.request_processor.RequestProcessor` instance
- ``resource``---a representation of the HTTP resource
- ``state``---the dictionary that contains the request state

Framework wrappers will add their own objects, as well.


--------------------
 Standard Renderers
--------------------

Aspen includes five renderers out of the box:

 - ``json_dump``---takes Python syntax, runs it through ``eval`` and then
   ``json.dumps``

 - ``jsonp_dump``---takes Python syntax, runs it through ``eval`` and
   ``json.dumps``, and then wraps it in a JSONP callback if one is specified in
   the querystring (as either ``callback`` or ``jsonp``)

 - ``stdlib_format``---takes a Python string, runs it through `format-style`_
   string replacement

 - ``stdlib_percent``---takes a Python string, runs it through `percent-style`_
   string replacement

 - ``stdlib_template``---takes a Python string, runs it through
   `template-style`_ string replacement


.. _format-style: https://docs.python.org/3.5/library/string.html#format-string-syntax
.. _percent-style: https://docs.python.org/3.5/library/stdtypes.html#printf-style-string-formatting
.. _template-style: https://docs.python.org/3.5/library/string.html#template-strings

.. note::

    Check the Aspen homepage for links to `plugins for other renderers`_.

    .. _plugins for other renderers: http://aspen.io/


-------------------
 Specline Defaults
-------------------

Speclines are optional. The defaults ... I guess we should point to the API
reference for this. And the framework wrappers will have something to say about
this, as well.


---------------------
 Content Negotiation
---------------------

Aspen negotiates with clients to determine how to best represent a resource for
a given request. Aspen models resources using simplates, and the content
sections of the simplate determine the available representations. Here are the
rules for negotiation:

#. **If the URL path includes a file extension**, Aspen looks in the Python
   mimetypes registry for a content type associated with the extension. If the
   extension is not in the registry, Aspen responds with ``404 Not Found``. If
   the extension *is* in the registry, Aspen looks for a match against the
   corresponding type. If no content section provides the requested
   representation, Aspen again responds with ``404 Not Found``.

#. **If the URL path does not include a file extension and there are multiple
   available types**, Aspen turns to the ``Accept`` header. If the ``Accept``
   header is missing or malformed, Aspen responds using the first available
   content section. If the ``Accept`` header is valid, Aspen looks for a match.
   If no content section provides an acceptable representation, Aspen responds
   with ``406 Not Acceptable``.

#. **If the URL path includes a file extension but there is only one available
   type**, then Aspen ignores the ``Accept`` header (as the spec `allows`_),
   responding with the only available representation.

.. note::

    Aspen delegates to the `python-mimeparse`_ library to determine the best
    available match for a given media range.

.. _python-mimeparse: https://pypi.python.org/pypi/python-mimeparse
.. _allows: https://tools.ietf.org/html/rfc7232#section-5.3.2
