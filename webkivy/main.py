# -*- coding: utf-8 -*-
import kivy
from webkivy.exception import show_exception, init_exception_handling

kivy.require('1.9.1')

import os
import json
import webbrowser

from kivy.uix.screenmanager import ScreenManager, Screen
import kivy.utils
from kivy.app import App
from kivy.lang import Builder

from webkivy.webloader import load_and_run


SETTINGS_FILE = "webkivy-settings.json"


if kivy.utils.platform == "android":
    from jnius import autoclass
    SETTINGS_FOLDER = autoclass('org.renpy.android.PythonActivity').mActivity.getFilesDir().getAbsolutePath()
else:
    SETTINGS_FOLDER = "."


HELP = """
Webkivy
---------------------------

This is a Python programming and prototyping tool using Kivy framework.

Quickly deploy your Android mobile application written in Python programming language over HTTP connection, wi-fi or any URL.

Copyright 2016 Mikko Ohtamaa. MIT licensed.
"""

# We first define our GUI
kv = '''
<LandingScreen>:
    AnchorLayout:
        anchor_y: 'top'
        anchor_x: 'center'
        padding: [20, 20, 20, 20]
        BoxLayout:
            id: stack
            orientation: 'vertical'
            spacing: 20
            TextInput:
                id: url
                size_hint_y: None
                height: self.minimum_height
                text: ''
            Button:
                text: 'Run script'
                size_hint_y: None
                on_release: app.run_script()
            Button:
                text: 'Help'
                size_hint_y: None
                on_release: app.show_help()
            Button:
                text: 'About the author'
                size_hint_y: None
                on_release: app.show_author()
            RstDocument:
                id: help
                text: ''
'''


class LandingScreen(Screen):
    pass


# Prepare kv for classes
Builder.load_string(kv)


class RemoteRunnerApp(App):
    """Simple application asking input URL where we fetch the Python script to run."""

    def run(self):
        self.read_settings()
        init_exception_handling()
        super(RemoteRunnerApp, self).run()

    def read_settings(self):
        """Read settings from .json file."""

        # TODO: Replace with Kivy's internal settings management?

        settings = None
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "rt") as f:
                    settings = json.load(f)
            except:
                pass

        if not settings:
            settings = {"url": "http://bit.ly/webkivytest#simplekivy:run"}

        self.settings = settings

    def run_script(self):
        self.write_settings()

        url = self.root.get_screen("landing").ids.url.text

        try:
            result = load_and_run(url)

            if not isinstance(result, Screen):
                raise RuntimeError("Entry point did not return kivy.uix.screenmanager.Screen")

            self.root.switch_to(result)

        except Exception as e:
            show_exception(e)

    def show_help(self):
        webbrowser.open("https://github.com/miohtama/android-remote-python")

    def show_author(self):
        webbrowser.open("https://opensourcehacker.com")

    def write_settings(self):
        root = self.root.get_screen("landing")
        self.settings["url"] = root.ids.url.text
        with open(SETTINGS_FILE, "wt") as f:
            json.dump(self.settings, f)

    def reset_landing_screen(self):

        root = LandingScreen(name="landing")
        root.ids.url.text = self.settings["url"]
        root.ids.help.text = HELP
        root.ids.help.colors.update({
            'background': '000000',
            'paragraph': 'eeeeee',
            'title': 'aaaaff',
            'bullet': '000000ff'})
        return root

    def build(self):
        sm = ScreenManager()
        sm.add_widget(self.reset_landing_screen())
        return sm


if __name__ == '__main__':
    RemoteRunnerApp().run()
