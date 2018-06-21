from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from functools import reduce
import os
import posixpath

from ..utils import Constant


def debug_noop(*args, **kwargs):
    pass


def debug_stdout(func):
    r = func()
    try:
        print("DEBUG: " + r)
    except Exception:
        print("DEBUG: " + repr(r))

debug = debug_stdout if 'ASPEN_DEBUG' in os.environ else debug_noop


def splitext(name):
    parts = name.rsplit('.', 1) + [None]
    return parts[:2]


def strip_matching_ext(a, b):
    """Given two names, strip a trailing extension iff they both have them.
    """
    aparts = splitext(a)
    bparts = splitext(b)

    def debug_ext():
        return "exts: %r( %r ) and %r( %r )" % (a, aparts[1], b, bparts[1])

    if aparts[1] == bparts[1]:
        debug(lambda: debug_ext() + " matches")
        return aparts[0], bparts[0]
    debug(lambda: debug_ext() + " don't match")
    return a, b


class DispatchStatus(object):
    """
    okay - found a matching leaf node
    missing - no matching file found
    unindexed - found a matching node, but it's a directory without an index
    """
    okay = Constant('okay')
    missing = Constant('missing')
    unindexed = Constant('unindexed')


DispatchResult = namedtuple('DispatchResult', 'status match wildcards extension canonical')
"""
    status - A DispatchStatus constant encoding the overall result
    match - the matching path (if status != 'missing')
    wildcards - a dict whose keys are wildcard names, and values are as supplied by the path
    extension - e.g. `json` when `foo.spt` is matched to `foo.json`
    canonical - the canonical path of the resource, e.g. `/` for `/index.html`
"""


MISSING = DispatchResult(DispatchStatus.missing, None, None, None, None)


class Dispatcher(object):
    """The abstract base class of dispatchers.

    :param www_root: the absolute path to a filesystem directory
    :param is_dynamic: a function that takes a file name and returns a boolean
    :param indices: a list of filenames that should be treated as directory indexes
    :param typecasters: a dict of typecasters, keys are strings and values are functions
    """

    def __init__(self, www_root, is_dynamic, indices, typecasters, **kw):
        self.www_root = os.path.realpath(www_root)
        self.is_dynamic = is_dynamic
        self.indices = indices
        self.typecasters = typecasters
        self.__dict__.update(kw)
        self.build_dispatch_tree()

    def build_dispatch_tree(self):
        """Abstract method called by :meth:`.__init__` to build the dispatch tree.
        """
        raise NotImplementedError('abstract method')

    def dispatch(self, path, path_segments):
        """Dispatch a request.

        :param str path: the request path, e.g. ``'/'``
        :param list path_segments: the path split into segments, e.g. ``['']``
        """
        raise NotImplementedError('abstract method')

    def find_index(self, dirpath):
        """Looks for an index file in a directory.
        """
        return _match_index(self.indices, dirpath)


class SystemDispatcher(Dispatcher):
    """Aspen's legacy dispatcher, not optimized for production use.
    """

    def build_dispatch_tree(self):
        """This method does nothing.
        """
        pass

    def dispatch(self, path, path_segments):
        listnodes = os.listdir
        is_leaf = os.path.isfile
        traverse = os.path.join
        result = _dispatch_abstract(
            listnodes, self.is_dynamic, is_leaf, traverse, self.find_index,
            self.www_root, path_segments,
        )
        debug(lambda: "dispatch_abstract returned: " + repr(result))

        # Protect against escaping the www_root.
        if result.match and not result.match.startswith(self.www_root):
            # Attempted breakout, e.g. a request for `/../secrets`
            return MISSING

        return result


def _dispatch_abstract(listnodes, is_dynamic, is_leaf, traverse, find_index, startnode, nodepath):
    """Given a list of nodenames (in 'nodepath'), return a DispatchResult.

    We try to traverse the directed graph rooted at 'startnode' using the
    functions:

       listnodes(joinedpath) - lists the nodes in the specified joined path

       is_dynamic(node) - returns true iff the specified node is dynamic

       is_leaf(node) - returns true iff the specified node is a leaf node

       traverse(joinedpath, newnode) - returns a new joined path by traversing
        into newnode from the current joinedpath

       find_index(joinedpath) - returns the index file in the specified path if
        it exists, or None if not

    Wildcards nodenames start with %. Non-leaf wildcards are used as keys in
    wildvals and their actual path names are used as their values. In general,
    the rule for matching is 'most specific wins': $foo looks for isfile($foo)
    then isfile($foo-minus-extension) then isfile(virtual-with-extension) then
    isfile(virtual-no-extension) then isdir(virtual)

    """
    nodepath = nodepath[:]  # copy it so we can mutate it if necessary
    wildvals, wildleafs = {}, {}
    curnode = startnode
    extension, canonical = None, None
    is_dynamic_node = lambda n: is_dynamic(traverse(curnode, n))
    is_leaf_node = lambda n: is_leaf(traverse(curnode, n))

    def get_wildleaf_fallback():
        lastnode_ext = splitext(nodepath[-1])[1]
        wildleaf_fallback = lastnode_ext in wildleafs or None in wildleafs
        if wildleaf_fallback:
            ext = lastnode_ext if lastnode_ext in wildleafs else None
            curnode, wildvals = wildleafs[ext]
            debug(lambda: "Wildcard leaf match %r and ext %r" % (curnode, ext))
            return DispatchResult(DispatchStatus.okay, curnode, wildvals, None, None)
        return None

    for depth, node in enumerate(nodepath):

        # check all the possibilities:
        # node.html, node.html.spt, node.spt, node.html/, %node.html/ %*.html.spt, %*.spt

        # don't serve hidden files
        subnodes = set([ n for n in listnodes(curnode) if not n.startswith('.') ])

        node_noext, node_ext = splitext(node)

        # only maybe because non-spt files aren't wild
        maybe_wild_nodes = [ n for n in sorted(subnodes) if n.startswith("%") ]

        wild_leaf_ns = [ n for n in maybe_wild_nodes if is_leaf_node(n) and is_dynamic_node(n) ]
        wild_nonleaf_ns = [ n for n in maybe_wild_nodes if not is_leaf_node(n) ]

        # store all the fallback possibilities
        remaining = reduce(posixpath.join, nodepath[depth:])
        for n in wild_leaf_ns:
            wildwildvals = wildvals.copy()
            k, v = strip_matching_ext(n[1:-4], remaining)
            wildwildvals[k] = v
            n_ext = splitext(n[:-4])[1]
            wildleafs[n_ext] = (traverse(curnode, n), wildwildvals)

        debug(lambda: "wildleafs is %r" % wildleafs)

        found_n = None
        last_node = (depth + 1) == len(nodepath)
        if last_node:
            debug(lambda: "on last node %r" % node)
            if node == '':  # dir request
                debug(lambda: "...last node is empty")
                path_so_far = traverse(curnode, node)
                index = find_index(path_so_far)
                if index:
                    debug(lambda: "found index: %r" % index)
                    return DispatchResult(DispatchStatus.okay, index, wildvals, None, canonical)
                if wild_leaf_ns:
                    found_n = wild_leaf_ns[0]
                    debug(lambda: "found wild leaf: %r" % found_n)
                    curnode = traverse(curnode, found_n)
                    node_name = found_n[1:-4]  # strip leading % and trailing .spt
                    wildvals[node_name] = node
                    return DispatchResult(DispatchStatus.okay, curnode, wildvals, None, canonical)
                debug(lambda: "no match")
                return DispatchResult(
                    DispatchStatus.unindexed, curnode + os.path.sep, None, None, canonical
                )
            elif node in subnodes and is_leaf_node(node):
                debug(lambda: "...found exact file, must be static")
                if is_dynamic_node(node):
                    return MISSING
                else:
                    found_n = node
                    if find_index(curnode) == traverse(curnode, node):
                        # The canonical path of `/index.html` is `/`
                        canonical = '/' + '/'.join(nodepath)[:-len(node)]
            elif node + ".spt" in subnodes and is_leaf_node(node + ".spt"):
                debug(lambda: "...found exact spt")
                found_n = node + ".spt"
            elif node_noext + ".spt" in subnodes and is_leaf_node(node_noext + ".spt") \
                    and node_ext:
                # node has an extension
                debug(lambda: "...found indirect spt, extension is `%s`" % node_ext)
                # indirect match - foo.spt is answering to foo.html
                extension = node_ext
                found_n = node_noext + ".spt"

            if found_n is not None:
                debug(lambda: "found_n: %r" % found_n)
                curnode = traverse(curnode, found_n)
            elif wild_nonleaf_ns:
                debug(lambda: "wild_nonleaf_ns")
                result = get_wildleaf_fallback()
                if result:
                    return result
                curnode = traverse(curnode, wild_nonleaf_ns[0])
                nodepath.append('')
                canonical = '/' + '/'.join(nodepath)
            elif node in subnodes:
                debug(lambda: "exact dirmatch")
                curnode = traverse(curnode, node)
                nodepath.append('')
                canonical = '/' + '/'.join(nodepath)
            else:
                debug(lambda: "fallthrough")
                result = get_wildleaf_fallback()
                if not result:
                    return MISSING
                return result

        if not last_node:  # not at last path seg in request
            debug(lambda: "on node %r" % node)
            if node in subnodes and not is_leaf_node(node):
                found_n = node
                debug(lambda: "Exact match " + repr(node))
                curnode = traverse(curnode, found_n)
            elif wild_nonleaf_ns:
                # need to match a wildnode, and we're not the last node, so we should match
                # non-leaf first, then leaf
                found_n = wild_nonleaf_ns[0]
                wildvals[found_n[1:]] = node
                debug(lambda: "Wildcard match %r = %r " % (found_n, node))
                curnode = traverse(curnode, found_n)
            else:
                debug(lambda: "No exact match for " + repr(node))
                result = get_wildleaf_fallback()
                if not result:
                    return MISSING
                return result

    return DispatchResult(DispatchStatus.okay, curnode, wildvals, extension, canonical)


def _match_index(indices, indir):
    """return the full path of the first index in indir, or None if not found"""
    for filename in indices:
        index = os.path.join(indir, filename)
        if os.path.isfile(index):
            return index
    return None
