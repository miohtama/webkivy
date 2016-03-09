===========================================================
Webkivy: Remote live edit of Python applications on Android
===========================================================

.. contents:: :local:

Introduction
============

Webkivy is a tool to execution `Python <https://python.org>`_ scripts on a mobile device over web. It is intended for quick prototyping, sharing your Python scripts with friends and learning Python development.

Live edit of source code is supported. You do not need to copy new application files to your phone by hand - it's enough to hit *Run* button again and again. This web like development model makes the prototyping life cycle fast. Furthermore no any development tools need to be installed lowering the barrier of entry for mobile application development.

The project is based on `Kivy <https://kivy.org/#home>`_ mobile application development framework. Using Python makes fast dynamic compiling and execution possible, something that's `difficult with statically typed Java toolchain <http://stackoverflow.com/q/17538537/315168>`_.

.. image:: screenshots/main.png

Supported platforms
===================

* Android (download)

* iOS (eventually)

Features
========

* "Just bunch of files" (JBOF) deployment model - use any hosting service or local wi-fi to serve your application without complexity of mobile application deployment

* Live reload of code

* Native access to Android APIs through `pyjnius <https://pyjnius.readthedocs.org/>`_: sensors, OpenGL, sound, others.

* User friendly Python exception handler - no need to dig Android logs to see Python traceback

Usage
=====

The application asks you for an URL where to load your Python script.

* The URL can be a link to a single .py file

* The URL can be a link to a folder (index.html file) containing references multiple .py files and other application resources like images and sounds.

* The URL must contain a fragment part telling the entry point. The entry point defines which Python module and function to call after the loading is complete.

* The URL may contain links to subfolders. These subfolders are also crawled and considered a Python submodule paths. Subfolders must come with their ``__init__.py`` file. Subfolder links must end with an ending slash (``/``) that is a default behavior of Python's simple HTTP server.

An example URL of running a Python application off from *gist.github.com*::

    https://gist.githubusercontent.com/miohtama/80391980c2e73b285cfe/raw/dd89a55497ba33a6014453d9bb7432ab424c01cf/kivyhello.py#main

An example URL of running a Python application from static web hosting with *index.html* support::

    http://bit.ly/webkivytest#simplekivy:run

The entry point function return `a Kivy screen object <https://kivy.org/docs/api-kivy.uix.screenmanager.html#kivy.uix.screenmanager.Screen>`_. Usually entry point is a module level function ``run()``. After entry point is called the Android application switches over to screen by given the entry point.

Running Python application from your local computer
---------------------------------------------------

* Assume you have created a Python file ``myscript.py`` based on the `example <https://github.com/miohtama/android-remote-python/blob/master/tests/test_data/simplekivy.py>`_.

* Make sure your phone and your computer are in same wi-fi network

* Figure out the internal IP address of your computer. Use the network manager of your operating system or following Python command::

     python -c "import socket ; print socket.gethostbyname(socket.gethostname())"

* Go to a folder where you have ``myscripy.py`` and start a Python built-in web server::

    python -m SimpleHTTPServer

* Enter URL to your computer. Replace ``999.999.999.999`` with your IP address

    http://999.999.999.999:8000/#myscript.py:run

* Hit *Run*

Entry point
===========

The Python entry point function is given in the URL fragment. It must return `a Kivy screen object <https://kivy.org/docs/api-kivy.uix.screenmanager.html#kivy.uix.screenmanager.Screen>`_. Usually entry point is a module level function ``run()``. After entry point is called the Kivy UI switches over to screen by given the entry point.

Example ``run`` entry point from ``http://localhost:8000#simplykivy:run``::

    from kivy.uix.screenmanager import Screen

    class HelloWorldScreen(Screen):

        def quit(self):
            # Bind this to your app UI if you want to return Webkivy main screen
            app = kivy.app.App.get_running_app()
            landing_screen = app.reset_landing_screen()
            self.manager.switch_to(landing_screen)

        def run():
            return HelloWorldScreen()


Exception handling
==================

By default all exceptions in Kivy main event loop are shown in a dialog:

.. image:: screenshots/exception.png

If you have code that may raise exception outside Kivy main loop you can decorate it with ``webkivy.exception.catch_gracefully` to get an error dialog. Otherwise you need to dig exception traceback from adb logs::


    from webkivy.exceptions catch_gracefully

    import android


    class MyScreen:

        def on_enter(self):
          android.activity.bind(on_new_intent=self.on_new_intent)

        @catch_gracefully()
        def on_new_intent(self, intent):

            action = intent.getAction()
            # Exception raised where here...


Installing packages
===================

Webkivy doesn't know about proper Python packaging (eggs, wheels, setup.py, etc.). However you can just symlink or copy related Python modules to your application as a subfolder. Subfolders are also crawled.

TODO: Currently this only works for submodules which use relative imports. Support for absolute imports is relatively easy (pun intended) to add.

Namespacing
===========

Your application may contain several modules. You should be able to import them using Python relative import::

    import .anothermodule

    from .anothermodule import foobar


In the case you need to use absolute imports modules are placed in ``webkivy.dynamic`` namespace.

Viewing logs
============

Android logs to a subsystem which is often referred as "adb logs". You will need to be able to read this when a Java native crash occurs e.g. when using Android APIs through pyjnius.

The easiest way to view these logs is to

* `Set your phone to developer mode <http://wccftech.com/enable-developer-options-in-android-6-marshmallow>`_

* `Install Android SDK <http://developer.android.com/sdk/index.html>`_

* Connect USB cable to your computer

* Use `adb logcat command <http://developer.android.com/tools/help/logcat.html>`_

Below is also a command line recipe if you are using a `Kivy Buildozer virtual machine <https://kivy.org/docs/guide/packaging-android-vm.html>`_.

Deploying on Android
====================

To build APK you need to use Buildozer virtual machine image (Linux).

`Make sure your phone is in developer mode <http://wccftech.com/enable-developer-options-in-android-6-marshmallow/>`_. Connect your phone. Expose your phone to the VM by clicking the USB icon in the lower right corner of Virtualbox. `Make sure you have high quality USB cable <http://stackoverflow.com/questions/21296305/adb-commandline-hanging-during-install-phonegap>`_.

Build debug APK::

    buildozer android debug

Make sure VM sees your connected Android phone::

    ﻿/home/kivy/.buildozer/android/platform/android-sdk-20/platform-tools/adb devices

Deploying on a local Android phone using Buildozer (VM)::

    buildozer android debug deploy run

For the first deployment it will ask permission on phone screen. Accept it and rerun the command.

When your application crashes you can view adb logs::

    ﻿/home/kivy/.buildozer/android/platform/android-sdk-20/platform-tools/adb logcat

Packaging for Google Play::

    pass


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

    kivy -m pytest tests

Run a single test::

    kivy -m pytest -k test_load_simple_module tests


Other
=====

Install jnius on OSX
--------------------

You get functioning import and autocompletion in your editor.

Example::

    git clone git@github.com:kivy/pyjnius.git
    find /Applications|grep -i "jni.h"
    # Oracly y u so fun
    ln -s /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/System/Library/Frameworks/JavaVM.framework/Versions/A/Headers/jni.h .
    /Applications/Kivy2.app/Contents/Resources/


    /Applications/Kivy2.app/Contents/Resources/venv/bin/python setup.py develop

`JNI headers installation on OSX <http://stackoverflow.com/questions/27498857/error-installing-pyjnius-jni-h-not-found-os-x-10-10-1>`_.

Reading list
============

* More complex Kivy application: https://github.com/tito/2048

