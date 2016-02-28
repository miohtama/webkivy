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
from kivy.properties import ObjectProperty

import android.activity
from jnius import autoclass
from jnius import cast

from webkivy.exception import catch_gracefully

from . import ndef

NfcAdapter = autoclass("android.nfc.NfcAdapter")
Toast = autoclass("android.widget.Toast")
PythonActivity = autoclass('org.renpy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
NdefRecord = autoclass('android.nfc.NdefRecord')
NdefMessage = autoclass('android.nfc.NdefMessage')
IsoDep = autoclass('android.nfc.tech.IsoDep')


Builder.load_string("""
<NFCScreen>:

    nfc_status: nfc_status

    BoxLayout:
        orientation: 'vertical'
        spacing: 40
        padding: 60
        RstDocument:
            id: nfc_status
            text: ''
        Button:
            text: 'Quit'
            on_press:
                self.parent.parent.quit()

""")



TAG_INFO = """
NFC tag found

Id: {tag_id}

Techs:

{techs}

"""


def byte_array_to_byte_string(bytes):
    s = "".join([chr(b) for b in bytes])
    return s


def byte_array_to_hex(bytes):
    s = byte_array_to_byte_string(bytes)
    return s.encode("hex")


class NFCScreen(Screen):

    nfc_status = ObjectProperty()

    def __init__(self):
        super(NFCScreen, self).__init__()

        #: android.nfc.NfcAdapter
        self.nfc_adapter = None

        self.found_sound = None

    def init_nfc(self):

        # http://code.tutsplus.com  /tutorials/reading-nfc-tags-with-android--mobile-17278
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

        # We get the following in adb logs and on_activity_result doesn't seem to work
        # ﻿W ActivityManager: startActivity called from non-Activity context; forcing Intent.FLAG_ACTIVITY_NEW_TASK for: Intent { act=android.nfc.action.TAG_DISCOVERED flg=0x20000000 cmp=com.opensourcehacker.webkivy/org.renpy.android.PythonActivity (has extras) }

        # android.activity.bind(on_activity_result=self.on_activity_result)
        # https://github.com/kivy/python-for-android/blob/master/pythonforandroid/recipes/android/src/android/activity.py
        android.activity.bind(on_new_intent=self.on_new_intent)

        Logger.info("NFC ready")

    @catch_gracefully()
    def on_new_intent(self, intent):

        # https://github.com/nadam/nfc-reader/blob/master/src/se/anyro/nfc_reader/TagViewer.java#L143

        action = intent.getAction()
        if action in [NfcAdapter.ACTION_TAG_DISCOVERED, NfcAdapter.ACTION_TECH_DISCOVERED, NfcAdapter.ACTION_NDEF_DISCOVERED]:

            # self.found_sound.play()
            id = intent.getByteArrayExtra(NfcAdapter.EXTRA_ID)
            tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG)

            # Get tag interfcae
            tag = cast("android.nfc.Tag", tag)

            tag_id = byte_array_to_hex(tag.getId())
            techs = tag.getTechList()
            techs = "".join(["* {}\n\n".format(t) for t in techs])

            self.nfc_status.text = TAG_INFO.format(tag_id=tag_id, techs=techs)

            if "android.nfc.tech.IsoDep" in tag.getTechList():
                self.nfc_status.text += self.extract_iso14443_info(tag)
                self.nfc_status.text += self.extract_credit_card_info(tag)

    def extract_iso14443_info(self, tag):
        iso = IsoDep.get(tag)

        max_bytes = iso.getMaxTransceiveLength()
        timeout = iso.getTimeout()

        return "Max bytes: {max_bytes}\n\nTimeout: {timeout} ms\n\n".format(**locals())


    def read_credit_card_file(self, iso, resp):
        """Read credit card data fiel off the the card."""

        # http://stackoverflow.com/questions/23107685/reading-public-data-of-emv-card/23113332#23113332

        text = ""

        # 00 B2 01 0C 00
        # B2 read record
        # 01 record number
        # 0C short fille identified (record number) shifted 4 bits left - http://www.openscdp.org/scripts/tutorial/emv/reademv.html
        # 00 max length

        apdu_cmd = [00, 0xB2, 0x01, 0x0C, 00]
        apdu_cmd_hex = [hex(c) for c in apdu_cmd]

        Logger.info("Sending read record command %s", apdu_cmd_hex)
        resp = iso.transceive(apdu_cmd)
        Logger.info("Received APDU response: %s", byte_array_to_hex(resp))

        bs = byte_array_to_byte_string(resp)
        return bs.decode("utf-8", "ignore")

    def extract_credit_card_info(self, tag):
        # https://github.com/AdamLaurie/RFIDIOt/blob/master/nfcid.py
        # https://github.com/doc-rj/smartcard-reader
        # https://github.com/thomaspatzke/android-nfc-paycardreader/blob/master/src/net/skora/eccardinfos/ECCardInfosActivity.java#L136
        # https://en.wikipedia.org/wiki/EMV
        # http://stackoverflow.com/questions/34196900/do-i-have-to-know-what-the-aid-of-a-card-is-for-card-emulation-with-android-hce

        iso = IsoDep.get(tag)
        iso.connect()

        try:

            found = False

            # Brute force AIDs
            for name, aid in AID_LIST:

                # APDU - Application Protocol Data Unit
                # When a remote NFC device wants to talk to your service, it sends a so-called "SELECT AID" APDU as defined in the ISO/IEC 7816-4 specification. The AID is an application identifier defined in ISO/IEC 7816-4.
                # http://developer.android.com/reference/android/nfc/cardemulation/HostApduService.html
                # http://www.openscdp.org/scripts/tutorial/emv/reademv.html

                # 00 header
                # A4 Select Command
                # 04 - Direct selection by DF name (data field=DF name) - http://www.cardwerk.com/smartcards/smartcard_standard_ISO7816-4_6_basic_interindustry_commands.aspx#table58
                # 00 - First record - http://www.cardwerk.com/smartcards/smartcard_standard_ISO7816-4_6_basic_interindustry_commands.aspx#table58
                # 07 (length)
                #

                aid_bytes = [ord(c) for c in aid.decode("hex")]

                assert len(aid_bytes) == 0x07, "Bad AID " + name

                apdu_cmd = [00, 0xA4, 0x04, 0x00, len(aid_bytes)] + aid_bytes

                apdu_cmd_hex = [hex(c) for c in apdu_cmd]
                Logger.info("Testing for %s, sending APDU command: %s", name, apdu_cmd_hex)

                resp = iso.transceive(apdu_cmd)
                Logger.info("Received APDU response: %s", byte_array_to_hex(resp))

                # Response is identified by its trailer status word
                # https://www.eftlab.com.au/index.php/site-map/knowledge-base/118-apdu-response-list
                # 90 SW1 Command successfully executed (OK).
                # 00 SW2 Command successfully executed (OK).
                if not (len(resp) > 2 and resp[-2] == 0x90 and resp[-1] == 00):
                    # Try next AID
                    continue

                # Other response is
                # https://blog.saush.com/2006/09/08/getting-information-from-an-emv-chip-card/

                credit_card_text = self.read_credit_card_file(iso, resp)

                text = "{}\n\n{}\n\n".format(name, credit_card_text)
                found = True

            if not found:
                text = "Not know credit card\n\n"

            return text


        finally:
            iso.close()

    def close_nfc(self):
        self.nfc_adapter.disableForegroundDispatch(PythonActivity.mActivity)
        android.activity.unbind(on_new_intent=self.on_new_intent)

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


# https://github.com/AdamLaurie/RFIDIOt/blob/master/nfcid.py
AID_LIST = 	[
		['MASTERCARD',		'a0000000041010'],
		['MASTERCARD',		'a0000000049999'],
		['VISA',		'a000000003'],
		['VISA Debit/Credit',	'a0000000031010'],
		['VISA Credit',		'a000000003101001'],
		['VISA Debit',		'a000000003101002'],
		['VISA Electron',	'a0000000032010'],
		['VISA V Pay',		'a0000000032020'],
		['VISA Interlink',	'a0000000033010'],
		['VISA Plus',		'a0000000038010'],
		['VISA ATM',		'a000000003999910'],
		['Maestro',		'a0000000043060'],
		['Maestro UK',		'a0000000050001'],
		['Maestro TEST',	'b012345678'],
		['Self Service',	'a00000002401'],
		['American Express',	'a000000025'],
		['ExpressPay',		'a000000025010701'],
		['Link',		'a0000000291010'],
	    ['Alias AID',		'a0000000291010'],
		['Cirrus',		'a0000000046000'],
		['Snapper Card',		'D4100000030001'],
		['Passport',		'A0000002471001'],
	    	]

