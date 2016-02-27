"""Simple NFC reader written in PYthon and Kivy."""

import os

import kivy.app
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader

from jnius import autoclass

NfcAdapter = autoclass("android.nfc.NfcAdapter")
Toast = autoclass("android.widget.Toast")
PythonActivity = autoclass('org.renpy.android.PythonActivity')


Builder.load_string("""
<NFCScreen>:
    BoxLayout:
        Label:
            text: 'NFC status: nothing'
        Button:
            text: 'Quit'
            on_press:
                self.parent.parent.quit()

""")


class NFCScreen(Screen):

    def init_nfc(self):
        activity = PythonActivity.mActivity
        adapter = NfcAdapter.getDefaultAdapter(activity)

        if not adapter:
            Toast.makeText(activity, "This device doesn't support NFC.", Toast.LENGTH_LONG).show()
            activity.finish()

    def init(self):
        self.init_nfc()

    def quit(self):
        """Switch back to the loader screen."""
        app = kivy.app.App.get_running_app()
        landing_screen = app.reset_landing_screen()
        self.manager.switch_to(landing_screen)

def run():
    screen = NFCScreen()
    screen.init()
    return screen