"""Packaged APK entry point for Kivy.

https://kivy.org/docs/guide/packaging-android.html#packaging-your-application-for-the-kivy-launcher
"""

import webkivy.main

app = webkivy.main.RemoteRunnerApp()
app.run()

