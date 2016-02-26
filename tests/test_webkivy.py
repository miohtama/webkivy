import subprocess
import os
import time

from webkivy.webloader import Loader
from webkivy.webloader import load_and_run
from webkivy.webloader import path_to_mod_name


def test_load_simple_module():
    # Simple module test - run function from web and see it matches expected value
    loader = Loader()
    main_fname = loader.load("https://gist.githubusercontent.com/miohtama/80391980c2e73b285cfe/raw/dd89a55497ba33a6014453d9bb7432ab424c01cf/kivyhello.py#main")
    mod = path_to_mod_name(main_fname)
    result = loader.run(mod, "hello")
    assert result == "Hello there"
    loader.close()


def test_load_crawl():
    # Simple module test - run function from web and see it matches expected value

    cmdline = ["kivy", "-m", "http.server", "8866"]

    web_server = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.join(os.getcwd(), "tests", "test_data"))
    try:

        # Let the web server wake up in another process
        time.sleep(1.0)

        web_server.poll()
        if web_server.returncode is not None:
            raise AssertionError("Web server process did not start up: {}".format(" ".join(cmdline)))

        loader = Loader()
        result = load_and_run("http://localhost:8866#hello1:hello")
        assert result == "Hello there"
    finally:
        web_server.terminate()
