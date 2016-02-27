===========================================================
Webkivy: Remote live edit of Python applications on Android
===========================================================

Webkivy applications allows execution of Python scripts on a mobile device over web. It is intended for quick prototyping, sharing your Python scripts with friends and learning about Python development.

Live edit of source code is supported. You do not need to copy new application files to your phone by hand - it's enough to hit *Run* button again and again. This web like development model makes the prototyping life cycle fast. Furthermore no any development tools need to be installed lowering the barrier of entry for mobile application development.

The project is based on `Kivy <https://kivy.org/#home>`_ mobile application development framework.

.. contents:: :local:

Supported platforms
===================

* Android (download)

* iOS (eventually)

Features
========

* "Just bunch of files" (JBOF) deployment model - use any hosting service or local wi-fi to serve your application without complexity

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

Namespacing
===========

Your application may contain several modules. You should be able to import them using Python relative import::

    import .anothermodule

    from .anothermodule import foobar


In the case you need to use absolute imports modules are placed in ``webkivy.dynamic`` namespace.

Viewing logs
============

Android logs to a subsystem which is often referred as "adb logs".

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

Packaging this for Android::

    pass

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

