Remote live edit of Python applications on Android
==================================================

This is a `Kivy based <https://kivy.org/#home>`_ Android application to run Python scripts over Internet connection. It allows you to quickly prototype Android applications by editing files using a local computer and running then on your phone.

Developing
==========

Setup package in development mode::

    kivy -m pip install -e ".[dev, test]"

Run tests::

    kivy -m pytest webkivy/tests

Please note that the project is not a proper distributed Python package, but a Kivy application.