# -*- coding: utf-8 -*-
"""Simple NFC reader written in Python and Kivy.


http://code.tutsplus.com/tutorials/reading-nfc-tags-with-android--mobile-17278

https://android.googlesource.com/platform/packages/apps/Nfc/+/master/src/com/android/nfc/NfcService.java

"""

import os

import kivy.app
from kivy import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty

import android.activity
from jnius import autoclass

from webkivy.exception import catch_gracefully

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

        self.found_sound = None

    def init_nfc(self):

        # http://code.tutsplus.com/tutorials/reading-nfc-tags-with-android--mobile-17278
        activity = PythonActivity.mActivity
        self.nfc_adapter = NfcAdapter.getDefaultAdapter(activity)

        if not self.nfc_adapter:
            Toast.makeText(activity, "This device doesn't support NFC.", Toast.LENGTH_LONG).show()
            activity.finish()

        if not self.nfc_adapter.isEnabled():
            self.nfc_status.text = "NFC not enabled"
        else:
            self.nfc_status.text = "NFC waiting for a touch"

        # https://github.com/nadam/nfc-reader/blob/master/src/se/anyro/nfc_reader/TagViewer.java#L75
        nfc_present_intent = Intent(activity, activity.getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        # http://cheparev.com/kivy-receipt-notifications-and-service/
        pending_intent = PendingIntent.getActivity(activity, 0, nfc_present_intent, 0)

        # http://developer.android.com/reference/android/nfc/NfcAdapter.html#enableForegroundDispatch%28android.app.Activity,%20android.app.PendingIntent,%20android.content.IntentFilter[],%20java.lang.String[][]%29
        self.nfc_adapter.enableForegroundDispatch(activity, pending_intent, None, None)

        # https://github.com/kivy/python-for-android/blob/master/pythonforandroid/recipes/android/src/android/activity.py

        # We get the following in adb logs and on_activity_result doesn't seem to work
        # ﻿W ActivityManager: startActivity called from non-Activity context; forcing Intent.FLAG_ACTIVITY_NEW_TASK for: Intent { act=android.nfc.action.TAG_DISCOVERED flg=0x20000000 cmp=com.opensourcehacker.webkivy/org.renpy.android.PythonActivity (has extras) }

        # android.activity.bind(on_activity_result=self.on_activity_result)
        android.activity.bind(on_new_intent=self.on_new_intent)

    @catch_gracefully
    def on_new_intent(self, intent):

        action = intent.getAction()
        if action in [NfcAdapter.ACTION_TAG_DISCOVERED, NfcAdapter.ACTION_TECH_DISCOVERED, NfcAdapter.ACTION_NDEF_DISCOVERED]:

            self.found_sound.play()

            raw_msgs = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
            Logger.info("Got %d raw msgs", len(raw_msgs))

            self.nfc_status.text = "NFC found"

        Logger.info(str(intent))

    def close_nfc(self):
        self.nfc_adapter.disableForegroundDispatch(PythonActivity.mActivity)
        android.activity.unbind(on_new_intent=self.on_new_intent)

    def on_pre_enter(self, *args):

        # Load fx
        my_path = os.path.dirname(__file__)
        sound_path = os.path.join(my_path, 'yay.mp3')
        self.found_sound = SoundLoader.load(sound_path)

    def on_enter(self):
        self.init_nfc()

    def on_leave(self):
        self.close_nfc()

    def quit(self):
        """Switch back to the loader screen."""
        app = kivy.app.App.get_running_app()
        landing_screen = app.reset_landing_screen()
        self.manager.switch_to(landing_screen)

def run():
    return NFCScreen()