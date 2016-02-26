Remote live edit of Python applications on Android
==================================================

This is a `Kivy based <https://kivy.org/#home>`_ Android application to run Python scripts over Internet connection. It allows you to quickly prototype Android applications by editing files using a local computer and running then on your phone.

Usage
=====

The application asks you for an URL where to load your Python script.

* The URL can be a link to single .py file

* The URL can be a link to a folder (index.html file) containing multiple .py files

* The URL must contain a fragment part telling which module and function to call

Examples URLs:


The entry point function return `a Kivy screen object <https://kivy.org/docs/api-kivy.uix.screenmanager.html#kivy.uix.screenmanager.Screen>`_. Usually entry point is a module level function ``run()``. After entry point is called the Android application switches over to screen by given the entry point.

Developing
==========

Setup package in development mode::

    kivy -m pip install -e ".[dev, test]"

Running Kivy application locally::

    kivy -m webkivy.main

Go to ``test_data`` folder and there start a web server ``kivy -m http.server 8866``.
Then you can use URL `http://localhost:8866/#simplekivy:main <http://localhost:8866/#simplekivy:run>`_ for local Kivy app testing.

Run tests::

    kivy -m pytest

Please note that the project is not a proper distributed Python package, but a Kivy application.