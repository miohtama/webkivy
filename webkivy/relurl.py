"""Relative URL utils."""

import urlparse
import posixpath


def get_relative_url(destination, source):
    """Get relative URL between two sources.

    http://stackoverflow.com/a/7469668/315168

    :param destination:
    :param source:
    :return: tuple (is same domain, relative url)
    """

    u_dest = urlparse.urlsplit(destination)
    u_src = urlparse.urlsplit(source)

    _uc1 = urlparse.urlunsplit(u_dest[:2]+tuple('' for i in range(3)))
    _uc2 = urlparse.urlunsplit(u_src[:2]+tuple('' for i in range(3)))

    if _uc1 != _uc2:
        ## This is a different domain
        return False, destination

    # If there is no / component in url assume it's root path
    src_path = u_src.path or "/"

    _relpath = posixpath.relpath(u_dest.path, posixpath.dirname(src_path))

    return True, _relpath
    # return True, urlparse.urlunsplit(('', '', _relpath, u_dest.query, u_dest.fragment))