###########################
 Filesystem Dispatch Rules
###########################

Aspen dispatches web requests to the filesystem based on paths. For simple
cases this is straightforward: ``/foo.html`` in the browser will find
``foo.html`` in the publishing root on your filesystem, and serve the file
statically. There are a couple wrinkles, however. What about *dynamic*
resources?  And what about variable path parts?

.. note::

    This is a tutorial. Please refer to our test table for the `complete dispatch rules`_.

    .. _complete dispatch rules:
        https://raw.githubusercontent.com/AspenWeb/aspen.py/master/tests/dispatch_table_data.rst


-------------------
 Dynamic Resources
-------------------

Sometimes you want the URL path ``/foo.html`` to find a static HTML file. More
frequently, you want it to serve a dynamic resource. Aspen uses the
`simplates`_ file format to model dynamic resources, and Aspen knows a file is
a simplate because of a ``.spt`` extension: ``/foo.html`` will find
``foo.html.spt`` if it exists. If you ask for ``/foo.html.spt`` directly,
however, you'll get a 404.

But what happens if you have both of the following on your filesystem?

 - ``foo.html``
 - ``foo.html.spt``

When you ask for ``/foo.html``, which one will you get? Which file will Aspen
use to represent the resource? The answer is ``foo.html``. The principle is
"most specific wins". The dynamic resource could actually serve other content
types (despite the ``.html`` in the filename), whereas the static resource will
*only* result in an HTML representation.

Now how about this one: what happens if you ask for ``/foo.html`` with *these*
two on your filesystem?

 - ``foo.html.spt``
 - ``foo.spt``

You guessed it: ``foo.html.spt``. Even though both are dynamic resources, and
both could technically result in any content type representation, the former is
likely to result in just HTML. Aspen therefore considers it to be more
specific, and to match it before the more general ``foo.spt``.

Now let's say you only have:

 - ``foo.spt``

That simplate will answer for ``/foo.html``. But! It will  *also* answer for
``/foo.json``, ``/foo.csv``, ``/foo.xml``, etc. One simplate can serve multiple
content type representations of the same resource. The `simplate docs`_ explain
how, but before we get there, let's talk about path variables.


----------------
 Path Variables
----------------

It's common in web applications to use parts of the URL path to pass variables
to a dynamic resource. For example, the ``2016`` in
``/blog/2016/some-post.html`` will want to end up as a ``year`` variable in
your code, and ``some-post`` perhaps as ``slug``. Since Aspen uses the
filesystem for dispatch, you define these variables on the filesystem. You use
the ``%`` (percent) character for this.

For the blog URL example, we might have the following simplate on our
filesystem:

 - ``blog/%year/%slug.html.spt``

Aspen matches from ``%`` to the end of the path part or a file extension,
whichever comes first. Now, inside your simplate, you will have access to
``year`` and ``slug`` variables containing the values from the URL path.


Typecasting
===========

URL path parts are strings, but sometimes you want to convert to a different
data type. Aspen provides for this by looking for special file extensions
following the ``%`` variable: ``.int`` and ``.float`` are supported by default.

If our simplate for the blog example was at:

 - ``blog/%year.int/%slug.html.spt``

Then the ``year`` variable inside our simplate would be an integer instead of a
string.


----------------------
 Ready for Simplates?
----------------------

Aspen serves static files directly, and dynamic files using simplates
(``.spt``), with path variables based on special ``%`` names on the filesystem.
With those basics in place, it's clearly time to `write a simplate`_!


.. _simplates:
.. _simplate docs:
.. _write a simplate:
    simplates.html
