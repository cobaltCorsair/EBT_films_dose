from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QFileInfo
import configparser

class MyQFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read('db_config.ini', encoding='cp1251')

    @staticmethod
    def getOpenFileName(*args, **kwargs):
        instance = MyQFileDialog()
        last_directory = instance.get_last_directory() if instance.should_use_last_directory() else ''
        kwargs['directory'] = kwargs.get('directory', last_directory)
        print(last_directory)
        file_path, _ = QFileDialog.getOpenFileName(*args, **kwargs)
        if file_path and instance.should_use_last_directory():
            instance.save_last_directory(file_path)
        return file_path, _

    def should_use_last_directory(self):
        try:
            return self.config.getboolean('DEFAULT', 'UseLastDirectory', fallback=False)
        except configparser.Error:
            return False

    def get_last_directory(self):
        try:
            return self.config['DEFAULT']['LastDirectory']
        except KeyError:
            return ''

    def save_last_directory(self, file_path):
        dir_path = QFileInfo(file_path).path()
        self.config['DEFAULT']['LastDirectory'] = dir_path
        with open('db_config.ini', 'w', encoding='cp1251') as configfile:
            self.config.write(configfile)
