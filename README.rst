===========================================================
Webkivy: Remote live edit of Python applications on Android
===========================================================

Webkivy applications allows execution of Python scripts on a mobile device over web. It is intended for quick prototyping, sharing your Python scripts with friends and learning about Python development.

Live edit of source code is supported. You do not need to copy new application files to your phone by hand - it's enough to hit *Run* button again and again. This web like development model makes the prototyping life cycle fast. Furthermore no any development tools need to be installed lowering the barrier of entry for mobile application development.

The project is based on `Kivy <https://kivy.org/#home>`_ mobile application development framework.

Supported platforms
===================

* Android (download)

* iOS (eventually)

Features
========

* "Just a bunch of files" deployment model - use any hosting service or local wi-fi to serve your application without complexity

* Live reload of code

* Native access to Android APIs through `pyjnius <https://pyjnius.readthedocs.org/>`: sensors, OpenGL, sound, others.

Usage
=====

The application asks you for an URL where to load your Python script.

* The URL can be a link to single .py file

* The URL can be a link to a folder (index.html file) containing references multiple .py files and other application resources like images and sounds

* The URL must contain a fragment part telling the entry point. The entry point defines which Python module and function to call after the loading is complete.

An example URL of running a Python application off from *gist.github.com*::

    https://gist.githubusercontent.com/miohtama/80391980c2e73b285cfe/raw/dd89a55497ba33a6014453d9bb7432ab424c01cf/kivyhello.py#main

An example URL of running a Python application from static web hosting with *index.html* support::

    https://bit.ly/webkivy#simplekivy:run

The entry point function return `a Kivy screen object <https://kivy.org/docs/api-kivy.uix.screenmanager.html#kivy.uix.screenmanager.Screen>`_. Usually entry point is a module level function ``run()``. After entry point is called the Android application switches over to screen by given the entry point.

Running Python application from your local computer
---------------------------------------------------

* Assume you have created a Python file ``myscript.py`` based on the `example <https://github.com/miohtama/android-remote-python/blob/master/tests/test_data/simplekivy.py>`_.

* Make sure your phone and your computer are in same wi-fi network

* Figure out the internal IP address of your computer. Use the network manager of your operating system or following Python command::

    python3 -c "import socket ; print(socket.gethostbyname(socket.gethostname()))"

* Go to a folder where you have ``myscripy.py`` and start a Python built-in web server::

    python3 -m http.server

* Enter URL to your computer. Replace ``999.999.999.999`` with your IP address

    http://999.999.999.999/#myscrit.py:run

* Hit *Run*

Developing Webkivy
==================

Please note that the project is not a proper distributed Python package, but a Kivy application.

Setup package in development mode::

    kivy -m pip install -e ".[dev, test]"

Running Kivy application locally::

    kivy -m webkivy.main

Go to ``test_data`` folder and there start a web server ``kivy -m http.server 8866``.
Then you can use URL `http://localhost:8866/#simplekivy:main <http://localhost:8866/#simplekivy:run>`_ for local Kivy app testing.

Run tests::

    kivy -m pytest

Deploying on a local Android phone using Buildozer (VM)::

    buildozer android debug deploy run

Packaging this for Android::

    pass