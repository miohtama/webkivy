"""Load remote Python classes from an URL and run them for Kivy on Android."""
import importlib
import os
import tempfile
import shutil
import sys
from urllib.parse import urlparse
from typing import Tuple

import lxml.html
import lxml.cssselect
import requests
from joblib import Parallel, delayed


#: Crawl all files with this extension from target
LOADABLE_SUFFIXES = [".py", ".kv"]


def get_url_fname(url):
    parts = urlparse(url)
    path = parts.path
    fname = os.path.basename(path)
    return fname


# http://stackoverflow.com/a/16696317/315168
def download_file(url, local_filename):
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

    return local_filename


def path_to_mod_name(mod_full_path):
    dir = os.path.dirname(mod_full_path)
    fname = os.path.basename(mod_full_path)
    base, ext = os.path.splitext(fname)
    return base


class UnsupportedURL(Exception):
    """We did not figure out how to run this URL."""


class Loader:
    """Helper class to load and run Python modules directly from web."""

    def __init__(self):
        self.path = tempfile.mkdtemp()

    def close(self):
        shutil.rmtree(self.path)

    def crawl(self, url):
        """Crawl .html page and extract all URls we think are part of application from there.

        Parallerize downloads using joblib.
        """

        def fetch_link(l):
            target = l["href"]
            fname = get_url_fname(url)
            _, ext = os.path.splitext(fname)
            if ext in LOADABLE_SUFFIXES:
                self.fetch_file(target)

        resp = requests.get(url)
        tree = lxml.html.fromstring(resp.content)
        links = tree.cssselect("a[href]")
        Parallel(n_jobs=4, backend="threading")(delayed(fetch_link)(l) for l in links)

    def fetch_file(self, url) -> Tuple[str]:
        fname = get_url_fname(url)
        dest = os.path.join(self.path, fname)
        download_file(url, dest)
        return dest

    def load(self, url) -> str:
        """Load script from URL."""

        fname = get_url_fname(url)
        _, ext = os.path.splitext(fname)
        if ext == ".py":
            py_file = self.fetch_file(url)
            return py_file
        else:
            self.crawl(url)

    def run(self, mod_name: str, func_name: str) -> object:
        if not dir in sys.path:
            sys.path.insert(0, dir)

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
    path = parts.path
    fragment = parts.fragment

    if fragment:
        if ":" not in fragment:
            raise UnsupportedURL("Fragment in URL {} was not format module_name:function_name".format(url))

        mod_name, func_name = fragment.split(":")
    else:
        if not path.endswith(".py"):
            raise UnsupportedURL("URL {} must contain module_name:function_name fragment or be direct .py link".format(url))

        mod_name = None
        func_name = "main"

    loader = Loader()
    main_fname = loader.load(url)
    if not mod_name:
        mod_name = path_to_mod_name(main_fname)
    return loader.run(mod_name, func_name)

