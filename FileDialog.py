import os

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QFileInfo
import configparser


class MyQFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        """
        Constructor method. Initializes a configparser instance and reads the configuration from 'db_config.ini'
        """
        super().__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read('db_config.ini', encoding='cp1251')

    @staticmethod
    def getFileName(func, *args, **kwargs):
        """
        Opens a file dialog and returns the selected file path along with other data.
        The file dialog starts at the last directory used, if the corresponding setting is enabled in the config file.

        :param func: The file dialog function to call (QFileDialog.getOpenFileName or QFileDialog.getSaveFileName).
        :param args: Positional arguments to pass to the file dialog function.
        :param kwargs: Keyword arguments to pass to the file dialog function.
        :return: The selected file path along with other data.
        """
        instance = MyQFileDialog()
        last_directory = instance.get_last_directory() if instance.should_use_last_directory() else ''
        kwargs['directory'] = kwargs.get('directory', last_directory)
        file_path, _ = func(*args, **kwargs)
        if file_path and instance.should_use_last_directory():
            instance.save_last_directory(file_path)
        return file_path, _

    @staticmethod
    def getOpenFileName(*args, **kwargs):
        """
        Wrapper for QFileDialog.getOpenFileName that supports the use of the last directory used.

        :param args: Positional arguments to pass to QFileDialog.getOpenFileName.
        :param kwargs: Keyword arguments to pass to QFileDialog.getOpenFileName.
        :return: The selected file path along with other data.
        """
        return MyQFileDialog.getFileName(QFileDialog.getOpenFileName, *args, **kwargs)

    @staticmethod
    def getSaveFileName(suggested_filename='', *args, **kwargs):
        """
        Wrapper for QFileDialog.getSaveFileName that supports the use of the last directory used and allows to suggest a filename.

        :param suggested_filename: A filename to suggest to the user.
        :param args: Positional arguments to pass to QFileDialog.getSaveFileName.
        :param kwargs: Keyword arguments to pass to QFileDialog.getSaveFileName.
        :return: The selected file path along with other data.
        """
        instance = MyQFileDialog()
        last_directory = instance.get_last_directory() if instance.should_use_last_directory() else ''
        kwargs['directory'] = os.path.join(last_directory, suggested_filename)
        return MyQFileDialog.getFileName(QFileDialog.getSaveFileName, *args, **kwargs)

    def should_use_last_directory(self):
        """
        Checks whether the 'UseLastDirectory' setting is enabled in the config file.

        :return: True if 'UseLastDirectory' is enabled, False otherwise.
        """
        try:
            return self.config.getboolean('DEFAULT', 'UseLastDirectory', fallback=False)
        except configparser.Error:
            return False

    def get_last_directory(self):
        """
        Wrapper for QFileDialog.getSaveFileName that supports the use of the last directory used and allows to suggest a filename.

        :param suggested_filename: A filename to suggest to the user.
        :param args: Positional arguments to pass to QFileDialog.getSaveFileName.
        :param kwargs: Keyword arguments to pass to QFileDialog.getSaveFileName.
        :return: The selected file path along with other data.
        """
        try:
            return self.config['DEFAULT']['LastDirectory']
        except KeyError:
            return ''

    def save_last_directory(self, file_path):
        """
        Saves the directory of the given file path as the last directory used in the config file.

        :param file_path: The file path whose directory should be saved.
        """
        dir_path = QFileInfo(file_path).path()
        self.config['DEFAULT']['LastDirectory'] = dir_path
        with open('db_config.ini', 'w', encoding='cp1251') as configfile:
            self.config.write(configfile)
