import ctypes
import os

from Warnings import Warnings


class IsAdmin:
    """
    A class for detecting administrator rights
    """

    @staticmethod
    def check_admin():
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        if is_admin:
            Warnings.error_if_is_admin()