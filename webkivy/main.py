import kivy
kivy.require('1.9.1')

import os
import json
import webbrowser

import kivy.utils
from kivy.app import App
from kivy.lang import Builder


SETTINGS_FILE = "webkivy-settings.json"


if kivy.utils.platform == "android":
    from jnius import autoclass
    SETTINGS_FOLDER = autoclass('org.kivy.android.PythonActivity').mActivity.getFilesDir().getAbsolutePath()
else:
    SETTINGS_FOLDER = "."


HELP = """
Python remote script runner
---------------------------

Run a .py script or multiple modules from a given URL
"""

# We first define our GUI
kv = '''
AnchorLayout:
    anchor_y: 'top'
    anchor_x: 'center'
    padding: [20, 20, 20, 20]
    BoxLayout:
        id: stack
        orientation: 'vertical'
        spacing: 20
        RstDocument:
            id: help
            text: ''
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
'''


class RemoteRunnerApp(App):
    """Simple application asking input URL where we fetch the Python script to run."""

    def run(self):
        self.read_settings()
        super().run()

    def read_settings(self):
        settings = None
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "rt") as f:
                    settings = json.load(f)
            except:
                pass

        if not settings:
            settings = {"url": "https://gist.github.com"}

        self.settings = settings

    def run_script(self):
        self.write_settings()
        url = self.root.ids.url.text
        pass

    def show_help(self):
        webbrowser.open("http://example.com")

    def write_settings(self):
        self.settings["url"] = self.root.ids.url.text
        with open(SETTINGS_FILE, "wt") as f:
            json.dump(self.settings, f)

    def build(self):
        root = Builder.load_string(kv)
        root.ids.url.text = self.settings["url"]
        root.ids.help.text = HELP
        root.ids.help.colors.update({
            'background': '000000',
            'paragraph': 'ffffff',
            'title': 'aaaaff',
            'bullet': '000000ff'})
        return root


if __name__ == '__main__':
    RemoteRunnerApp().run()
