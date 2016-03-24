# -*- coding: utf-8 -*-
"""Load remote Python classes from an URL and run them for Kivy on Android.

.. note ::

    We do not claim to offer perfect functionality, just enough to get your few .py files and images into your phone.

"""

from __future__ import print_function

import concurrent.futures
import cgi
import importlib
import os
import tempfile
import shutil
import sys
from six.moves.urllib.parse import urlparse, urljoin

import atexit
import lxml.html
import lxml.cssselect
import requests

from .relurl import get_relative_url


#: Fetch all files with this extension from crawl target
LOADABLE_SUFFIXES = [".py", ".kv", ".wav", ".mp3", ".png", ".jpg", ".gif"]


#: sys.path reset state
original_sys_path = None

#: sys.module reset state
original_modules = None


def record_original_modules():
    """This allows us to reload/reset."""
    global original_sys_path
    global original_modules

    if not original_modules:
        original_modules = sys.modules

    if not original_sys_path:
        original_sys_path = sys.path


def get_url_fname(url):
    parts = urlparse(url)
    path = parts.path
    fname = os.path.basename(path)
    return fname


def get_response_fname(resp):
    # See if we can get filename from content disposition header
    # (usually indicates raw download on pastebins)
    fname = None
    cd = resp.headers.get("content-disposition")
    if cd:
        value, params = cgi.parse_header(cd)
        fname = params.get("filename")

    # Next best guess
    if not fname:
        fname = get_url_fname(resp.url)

    return fname

# http://stackoverflow.com/a/16696317/315168
def download_file(url, target_path):
    r = requests.get(url, stream=True, timeout=60.0)

    fname = get_response_fname(r)

    target_file = os.path.join(target_path, fname)
    with open(target_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

    return target_file


def path_to_mod_name(mod_full_path):
    dir = os.path.dirname(mod_full_path)
    fname = os.path.basename(mod_full_path)
    base, ext = os.path.splitext(fname)
    return base


def is_likely_app_part(link, base_url):

    # assume this is subfolder
    if link.endswith("/"):
        is_relative, rel_path = get_relative_url(link, base_url)

        if not is_relative:
            # Different domain
            return False

        if not rel_path.startswith(".."):
            return True

    fname = get_url_fname(link)
    _, ext = os.path.splitext(fname)
    ext = ext.lower()
    return ext in LOADABLE_SUFFIXES


class UnsupportedURL(Exception):
    """We did not figure out how to run this URL."""


class Loader(object):
    """Helper class to load and run Python modules directly from web.

    * Discriminates Python modules and index listings based on file extension and content-disposition

    * Creates a root folder with with __init__.py where Python modules are placed

    * Crawls HTML for .py and resource links

    * Crawls HTML for subfolders

    * Parallel download of files
    """

    def __init__(self):

        # This is where our Python package is based
        self.temp_path = tempfile.mkdtemp()

        #: List of already loaded urls so we don't follow to same submodule targets twice
        self.loaded = set()

        # Create a special package where downloaded files are placed. This is to make relative imports to work.
        self.path = os.path.join(self.temp_path, "python_root")
        os.makedirs(self.path)
        open(os.path.join(self.path, "__init__.py"), 'a').close()

    def close(self):
        shutil.rmtree(self.temp_path)

        if self.temp_path in sys.path:
            sys.path.remove(self.temp_path)

    def crawl(self, url, base_url):
        """Crawl .html page and extract all URls we think are part of application from there.

        Parallerize downloads using threads.
        """

        resp = requests.get(url)

        # See through redirects
        final_base_url = resp.url

        tree = lxml.html.fromstring(resp.content)
        elems = tree.cssselect("a")
        links = [urljoin(final_base_url, elem.attrib.get("href", "")) for elem in elems]
        links = [link for link in links if is_likely_app_part(link, base_url)]

        # Load all links paraller
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.fetch_file, link, base_url): link for link in links}
            for future in concurrent.futures.as_completed(future_to_url):
                future.result()  # Raise exception in main thread if bad stuff happened

    def fetch_file(self, url, base_url, should_not_be_html=True):
        """Fetch a Python module or data file"""

        # Bookkeeping across crawled threads
        if url in self.loaded:
            return

        self.loaded.add(url)

        # Assume subfolder, not direct saveable file
        if url.endswith("/"):
            self.crawl(url, base_url)
            return

        same_domain, rel_path = get_relative_url(url, base_url)

        # Make oo sounds
        assert same_domain, "Whoops how we ended up at {} when base_url is {}".format(url, base_url)
        assert not rel_path.startswith(".."), "Ooops somehow ended up level below base url: {} -> {} path: {}".format(base_url, url, rel_path)

        target_path = os.path.join(self.path, rel_path)
        target_path = os.path.dirname(target_path)

        try:
            os.makedirs(target_path)
        except OSError:
            # Python 2 does not have exist_ok yet :<
            pass

        target_file = download_file(url, target_path)

        print("Downloaded {} to {}".format(url, target_file))

        f = open(target_file, "rt")
        payload = f.read(512).lower()
        if "<!doctype html" in payload or "<html" in payload:
            # Likely an error page
            raise UnsupportedURL("Got a likely an error page for URL instead of a Python module {}: {}".format(url, payload))

        return target_file

    def load(self, url):
        """Load script from URL."""

        # Check for a redirect to get a final base_url where to start

        resp = requests.head(url, allow_redirects=True)
        if url != resp.url:
            # Followed a redirect
            url = resp.url

        fname = get_response_fname(resp)
        _, ext = os.path.splitext(fname)

        if ext == ".py":
            py_file = self.fetch_file(url, url)
            return py_file
        else:
            self.crawl(url, url)

    def run(self, mod_name, func_name):
        global original_sys_path
        global original_modules

        record_original_modules()

        # Kind of brute force approach to get rid of old modules, seems to work
        sys.path = original_sys_path
        sys.path.insert(0, os.path.join(self.temp_path, "python_root"))

        for mod in sys.modules:
            if mod not in original_modules:
                del sys.modules[mod]

        # Use a special package name where downloaded modules are placed
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name, None)
        assert func, "Module {} doesn't contain function {}".format(mod, func_name)
        return func()


def load_and_run(url):
    """Load URL.

    URL can be a Python file (detected if it ends .py) or any HTML file. Example::

    In the case of HTML file it is crawled from all files ending .py, those are downloaded and one separated by a URL fragment is run. Example::

        http://192.168.0.1/myfolder#main.py

    The main module must contain kivy() function which returns a Kivy layout object. After loading this layout will take over the current layout.

    .. note ::

        This function will leave temporary files around
    """

    parts = urlparse(url, allow_fragments=True)
    fragment = parts.fragment

    if not fragment:
        raise UnsupportedURL("URL must contain fragment telling entry point function: {}".format(url))

    if ":" in fragment:
        mod_name, func_name = fragment.split(":")
    else:
        mod_name = None
        func_name = fragment

    loader = Loader()
    main_fname = loader.load(url)
    if not mod_name:
        mod_name = path_to_mod_name(main_fname)

    try:
        return loader.run(mod_name, func_name)
    finally:
        # Don't leave tmp directory right away as it may contain resource files (graphics, audio) still needed to load
        atexit.register(loader.close)


