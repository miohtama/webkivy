"""Graceful Python exception handling."""
import traceback
import functools

from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from kivy.base import ExceptionHandler
from kivy.base import ExceptionManager


IGNORE_EXCEPTIONS = (KeyboardInterrupt, MemoryError,)


def show_exception(e):
    """Show th latest exception in a pop-up dialog."""
    tb = traceback.format_exc()
    Logger.exception(str(e))
    Logger.exception(tb)
    popup = Popup(title='Python exception occured',
        content=TextInput(text=str(e) + "\n\n" + tb),
        size_hint=(.8, .8))
    popup.open()


class PopUpHandler(ExceptionHandler):
    """Kivy exception handler to show error in a dialog."""

    def handle_exception(self, e):
        show_exception(e)
        if isinstance(e, IGNORE_EXCEPTIONS):
            # Let the user to quit the application with CTRL+C
            return ExceptionManager.RAISE
        else:
            return ExceptionManager.PASS


def init_exception_handling():
    ExceptionManager.add_handler(PopUpHandler())


def catch_gracefully():
    """Function decorator to show any Python exceptions occured inside a function in a pop-up dialog.

    Use then the function call path does not go through Kivy main thread and Kivy exception handler.

    """
    def _outer(func):

        @functools.wraps(func)
        def _inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, IGNORE_EXCEPTIONS):
                    raise
                else:
                    show_exception(e)

        return _inner

    return _outer

