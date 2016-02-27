"""Graceful Python exception handling."""
import traceback

from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from kivy.base import ExceptionHandler
from kivy.base import ExceptionManager


def show_exception(e):
    """Show th latest exception in a pop-up dialog."""
    tb = traceback.format_exc()
    Logger.exception(str(e))
    Logger.exception(tb)
    popup = Popup(title='Python exception occured',
        content=TextInput(text=str(e) + "\n\nSee adb logs for details\n\n" + tb),
        size_hint=(.8, .8))
    popup.open()


class PopUpHandler(ExceptionHandler):
    """Kivy exception handler to show error in a dialog."""

    def handle_exception(self, e):
        show_exception(e)
        if isinstance(e, (KeyboardInterrupt, MemoryError,)):
            return ExceptionManager.RAISE
        else:
            return ExceptionManager.PASS


def init_exception_handling():
    ExceptionManager.add_handler(PopUpHandler())