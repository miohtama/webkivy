"""Simple NFC reader written in Python and Kivy.

http://code.tutsplus.com/tutorials/reading-nfc-tags-with-android--mobile-17278


"""

import os

import kivy.app
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty

from jnius import autoclass

NfcAdapter = autoclass("android.nfc.NfcAdapter")
Toast = autoclass("android.widget.Toast")
PythonActivity = autoclass('org.renpy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')


Builder.load_string("""
<NFCScreen>:

    nfc_status: nfc_status

    BoxLayout:
        Label:
            id: nfc_status
            text: ''
        Button:
            text: 'Quit'
            on_press:
                self.parent.parent.quit()

""")


class NFCScreen(Screen):

    nfc_status = ObjectProperty()

    def __init__(self):
        super(NFCScreen, self).__init__()

        #: android.nfc.NfcAdapter
        self.nfc_adapter = None

    def init_nfc(self):

        # http://code.tutsplus.com/tutorials/reading-nfc-tags-with-android--mobile-17278
        activity = PythonActivity.mActivity
        self.nfc_adapter = NfcAdapter.getDefaultAdapter(activity)

        if not adapter:
            Toast.makeText(activity, "This device doesn't support NFC.", Toast.LENGTH_LONG).show()
            activity.finish()

        if not adapter.isEnabled():
            self.nfc_status.text = "NFC not enabled"
        else:
            self.nfc_status.text = "NFC waiting for a touch"

        # https://github.com/nadam/nfc-reader/blob/master/src/se/anyro/nfc_reader/TagViewer.java#L75
        pending_intent = PendingIntent.getActivity(activity, 0, Intent(activity, activity.getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), 0)

        # http://developer.android.com/reference/android/nfc/NfcAdapter.html#enableForegroundDispatch%28android.app.Activity,%20android.app.PendingIntent,%20android.content.IntentFilter[],%20java.lang.String[][]%29
        self.nfc_adapter.enableForegroundDispatch(activity, pending_intent, None, None)

    def close_nfc(self):
        self.nfc_adapter.disableForegroundDispatch(PythonActivity.mActivity)

    def on_leave(self):
        self.close_nfc()

    def quit(self):
        """Switch back to the loader screen."""
        app = kivy.app.App.get_running_app()
        landing_screen = app.reset_landing_screen()
        self.manager.switch_to(landing_screen)

def run():
    screen = NFCScreen()
    screen.init_nfc()
    return screen