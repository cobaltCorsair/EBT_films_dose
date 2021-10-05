# Python 3.7
# -*- coding: utf-8 -*-
import sys

import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import os
import tifffile as tifimage
from scipy.optimize import curve_fit

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLineEdit, QCheckBox, QDoubleSpinBox
from Dose import Ui_MainWindow
from calibrate_list import Ui_Form


class Dose:
    """
    Calculate dose
    """

    def __init__(self, zero_dose, calibrate_list, irradiation_film, sigma):
        self.zero_dose = zero_dose
        self.calibrate_list = calibrate_list
        self.irradiation_film = irradiation_film
        self.sigma = sigma

        self.od_blank = None
        self.p_opt = None

    def fit_func(self, od, a, b, c):
        """
        Fitting function for calibration curve
        :param od:
        :param a:
        :param b:
        :param c:
        :return:
        """
        return (b / (od - a)) + c

    def red_chanel_calc(self):
        """
        Calculate value in red chanel of blank field
        :return:
        """
        blankFieldPath = self.zero_dose
        im = tifimage.imread(blankFieldPath)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        odBlank = np.mean(imarray)
        print("Blank field value: ", round(odBlank, 2))

        self.od_blank = odBlank
        return odBlank

    def find_best_fit(self, pathToFilm, odZeroDose, odBlank):
        """
        Find best fit to dose-OD points
        """
        # Тут должен быть обработчик для каждого файла из списка
        # Берем каждый файл из словаря, обрабатываем его в соответствии с формулой
        '''
        odBlank: среднее значение красного канала "пустого поля"
        odZeroDose: для этого числа лучше завести копию этой функции без последней строки
                    это значение дальше используем внутри функции
        '''

        im = tifimage.imread(pathToFilm)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        odCurrentDose = np.mean(imarray)
        odCurrentDose = np.log10(odBlank / odCurrentDose)
        odCurrentDose = odCurrentDose - odZeroDose

        return odCurrentDose
    #
    # def draw_curve(self):
    #     """
    #
    #     """
    #     popt, pcov = curve_fit(self.fit_func, calibrList[:, 0], calibrList[:, 1], sigma=calibrList[:, 0] * self.sigma)
    #
    #     fig, ax = plt.subplots(figsize=(9, 5))
    #     ax.plot(calibrList[:, 0], calibrList[:, 1], ".k", markersize=6, label="Измерения")
    #     ax.plot(calibrList[:, 0], self.fit_func(calibrList[:, 0], *popt))
    #     # ax.set_xlim(5000,44000)
    #     # ax.set_ylim(-1,np.amax(calibrList[;,1])+1)
    #     ax.grid(True, linestyle="-.")
    #     ax.set_ylabel('Поглощенная доза, Гр')
    #     ax.set_xlabel('Относительная оптическая плотность')
    #     plt.show()
    #
    #     self.p_opt = popt
    #
    # def user_image(self):
    #     """
    #     Working with user image
    #     """
    #     userImg = self.irradiation_film
    #     im = tifimage.imread(userImg)
    #     imarray = np.array(im, dtype=np.uint16)
    #     imarray = (imarray[:, :, 0])
    #
    #     print("\nShape of scanned film:", np.shape(imarray))
    #
    #     z = []
    #     counter = 0
    #     print("\nPrepearing your file:\n")
    #
    #     for i in np.nditer(imarray):
    #         x = np.log10(self.od_blank / i)
    #         x = x - self.zero_dose
    #         x = self.fit_func(x, *self.p_opt)
    #         z = np.append(z, x)
    #
    #         counter = counter + 1
    #         if counter % 10000 == 0:
    #             print("Iteration ", counter, "/", np.size(imarray))
    #
    #     z = z.reshape(np.shape(imarray))
    #     print("\nDose calculation ended!!!\n")
    #
    #     fig, ax1 = plt.subplots(figsize=(9, 5))
    #     im3 = ax1.imshow(z, cmap="jet", vmin=0, vmax=2., interpolation="gaussian")
    #     cbar = fig.colorbar(im3, ax=ax1, orientation="vertical")
    #     plt.show()


class Form(QtWidgets.QWidget, Ui_Form):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.widget_count = 0
        self.all_widgets = None

        self.pushButton.clicked.connect(lambda: self.get_empty_field_file(self.lineEdit))
        self.pushButton_2.clicked.connect(self.dynamic_add_fields)
        self.pushButton_3.clicked.connect(self.dynamic_delete_fields)
        self.pushButton_4.clicked.connect(self.get_all_params_widgets)

    def search_file(self):
        """Поиск файла"""
        file_name = QFileDialog.getOpenFileName(self, 'Открыть файл', "*.tif")[0]
        return file_name

    def get_empty_field_file(self, line):
        line.setText(self.search_file())

        if len(line.text()) != 0:
            line.setDisabled(True)

    def dynamic_add_fields(self):
        spin_box = QtWidgets.QDoubleSpinBox()
        qline_edit = QtWidgets.QLineEdit()
        push_button = QtWidgets.QPushButton("Select")

        self.gridLayout_3.addWidget(spin_box)
        self.gridLayout_3.addWidget(qline_edit)
        self.gridLayout_3.addWidget(push_button)

        #push_button.clicked.connect(self.search_file)
        push_button.clicked.connect(lambda: self.get_empty_field_file(qline_edit))

        self.widget_count += 1

    def dynamic_delete_fields(self):
        index = self.gridLayout_3.count()
        if index != 5:
            for i in range(3):
                index -= 1
                myWidget = self.gridLayout_3.itemAt(index).widget()
                myWidget.setParent(None)
                self.adjustSize()
                print(index)

    def get_all_params_widgets(self):
        doses = []
        paths = []
        widgets = (self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count()))
        self.all_widgets = widgets
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                print("Linedit: %s" % widget.text())
                doses.append(widget.text())
            if isinstance(widget, QDoubleSpinBox):
                paths.append(widget.value())
                print("SpinBox: %s" % widget.value())
        print(doses)
        print(paths)


class CalcUI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(CalcUI, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.form = None

        self.empty_field_file = None
        # empty field
        self.ui.pushButton_5.clicked.connect(self.get_empty_field_file)
        self.ui.pushButton_8.clicked.connect(self.get_dialog_window)

    def get_empty_field_file(self):
        self.ui.lineEdit_2.setText(self.search_file())

        if len(self.ui.lineEdit_2.text()) != 0:
            self.empty_field_file = self.ui.lineEdit_2.text()
            self.ui.lineEdit_2.setDisabled(True)
            # start
            self.start_calc()

    def get_dialog_window(self):
        self.form = Form()
        self.form.show()

    def search_file(self):
        """Поиск файла"""
        file_name = QFileDialog.getOpenFileName(self, 'Открыть файл', "*.tif")[0]
        return file_name

        # if len(self.ui.lineEdit_3.text()) != 0:
        #     self.forums_list = self.ui.lineEdit_3.text()
        #     return True

    def start_calc(self):
        Dose(self.empty_field_file, '', '', 0).red_chanel_calc()


app = QtWidgets.QApplication([])
# иконка приложения
# ico = QtGui.QIcon('./src/icon.png')
# app.setWindowIcon(ico)
# стиль отображения интерфейса
app.setStyle("Fusion")
app.processEvents()
application = CalcUI()

# указываем заголовок окна
application.setWindowTitle("Dose")
# задаем минимальный размер окна, до которого его можно ужимать
# application.setMaximumSize(800, 600)
application.show()
sys.exit(app.exec())
