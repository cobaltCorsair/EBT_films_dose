import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        # Получаем путь к изображению сплэша
        if getattr(sys, 'frozen', False):
            # Если приложение скомпилировано
            application_path = sys._MEIPASS
        else:
            # Если приложение запущено из исходников
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        splash_path = os.path.join(application_path, 'sources', 'splash.png')
        
        # Создаем сплэш с изображением
        super().__init__(QtGui.QPixmap(splash_path))
        
        # Устанавливаем флаг, чтобы окно было поверх всех остальных
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint) 
        
    def close_splash(self):
        """
        Метод для закрытия splash-экрана
        """
        self.close() 