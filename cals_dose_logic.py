# Python 3.7
# -*- coding: utf-8 -*-
import random
import sys

import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import os
import tifffile as tifimage
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from numpy import ndarray
from scipy.optimize import curve_fit

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLineEdit, QCheckBox, QDoubleSpinBox, QSizePolicy, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from Dose import Ui_MainWindow
from calibrate_list import Ui_Form


class Dose:
    """
    Calculate dose
    """

    def __init__(self, zero_dose, calibrate_list, doses_list, irradiation_film, sigma):
        self.zero_dose = zero_dose
        self.calibrate_list = calibrate_list
        self.irradiation_film = irradiation_film
        self.setting_doses = doses_list
        self.sigma = sigma

        self.calculation_doses = []

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

    def calc_dose(self, path_to_film):
        """
        Обработчик файлов снимков
        """
        im = tifimage.imread(path_to_film)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        od_current_dose = np.mean(imarray)
        od_current_dose = np.log10(self.od_blank / od_current_dose)

        return od_current_dose

    def find_best_fit(self, path_to_film):
        od_current_dose = self.calc_dose(path_to_film) - self.zero_dose
        # print(od_current_dose)
        self.calculation_doses.append(od_current_dose)
        # return od_current_dose

    def calculate_calibrate_film(self):
        # сначала считаем нулевую дозу
        self.zero_dose = self.calc_dose(self.zero_dose)
        # затем считаем для каждого файла с использованием посчитанной нулевой
        for i in self.calibrate_list:
            self.find_best_fit(i)

        p_opt, p_cov = curve_fit(self.fit_func, np.array(self.calculation_doses), np.array(self.setting_doses),
                               sigma=np.array(self.calculation_doses) * (self.sigma / 100))
        self.p_opt = p_opt

    def draw_curve(self):
        #fig, ax = plt.subplots(figsize=(9, 5))
        ax = application.figure_graph.add_subplot(111)
        ax.plot(self.calculation_doses, self.setting_doses, ".k", markersize=6, label="Измерения")
        ax.plot(self.calculation_doses, self.fit_func(self.setting_doses, *self.p_opt))
        ax.grid(True, linestyle="-.")
        ax.set_ylabel('Поглощенная доза, Гр')
        ax.set_xlabel('относительная оптическая плотность')
        application.canvas_graph.draw()
        #plt.show()

    def draw_dose_map(self):
        """
        Working with user image
        """
        userImg = self.irradiation_film
        im = tifimage.imread(userImg)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])

        print("\nShape of scanned film:", np.shape(imarray))

        z = []
        counter = 0
        print("\nPrepearing your file:\n")

        for i in np.nditer(imarray):
            x = np.log10(self.od_blank / i)
            x = x - self.zero_dose
            x = self.fit_func(x, *self.p_opt)
            z = np.append(z, x)

            counter = counter + 1
            if counter % 10000 == 0:
                print("Iteration ", counter, "/", np.size(imarray))

        z = z.reshape(np.shape(imarray))
        print("\nDose calculation ended!!!\n")

        #fig, ax = plt.subplots(figsize=(9, 5))
        ax = application.figure_map.add_subplot(111)
        im3 = ax.imshow(z, cmap="jet", vmin=0, vmax=2., interpolation="gaussian")
        application.figure_map.colorbar(im3, ax=ax, orientation="vertical")
        application.canvas_map.draw()
        #plt.show()

class DosesAndPaths:
    doses = list()
    paths = list()
    sigma = int()


class Form(QtWidgets.QWidget, Ui_Form):
    openDialog = pyqtSignal()

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
        file_name = QFileDialog.getOpenFileName(self, 'Открыть файл', '', '*.tif', None, QFileDialog.DontUseNativeDialog)[0]
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

        # push_button.clicked.connect(self.search_file)
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
        sigma = self.spinBox.value()
        widgets = (self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count()))
        self.all_widgets = widgets
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                print("Linedit: %s" % widget.text())
                paths.append(widget.text())
            if isinstance(widget, QDoubleSpinBox):
                doses.append(widget.value())
                print("SpinBox: %s" % widget.value())

        DosesAndPaths.doses = doses
        DosesAndPaths.paths = paths
        DosesAndPaths.sigma = sigma

    def create_widgets_second_open(self):
        data_count = len(DosesAndPaths.doses)
        print(data_count)
        if self.gridLayout_3.count() >= 5 and data_count > 1:
            for i in range(data_count - 1):
                self.dynamic_add_fields()

    def closeEvent(self, event):
        self.openDialog.emit()


class CalcUI(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(CalcUI, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.form = None

        # self.figure_graph = plt.figure()
        # self.canvas_graph = FigureCanvas(self.figure_graph)
        # self.toolbar_graph = NavigationToolbar(self.canvas_graph, self)
        # self.ui.verticalLayout.addWidget(self.toolbar_graph)
        # self.ui.verticalLayout.addWidget(self.canvas_graph)

        self.scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        self.ui.graphicsView.setScene(self.scene)

        self.figure_map = plt.figure()
        self.canvas_map = FigureCanvas(self.figure_map)
        self.toolbar_map = NavigationToolbar(self.canvas_map, self)
        self.ui.verticalLayout_2.addWidget(self.toolbar_map)
        self.ui.verticalLayout_2.addWidget(self.canvas_map)

        # empty field
        self.empty_field_file = None
        # irradiate film
        self.irrad_film_file = None

        self.ui.pushButton_5.clicked.connect(self.get_empty_field_file)
        self.ui.pushButton_7.clicked.connect(self.get_irrad_film_file)
        self.ui.pushButton_8.clicked.connect(self.get_dialog_window)
        self.ui.pushButton_4.clicked.connect(self.start_calc)

    def get_irrad_film_file(self):
        self.ui.lineEdit_3.setText(self.search_file())

        if len(self.ui.lineEdit_3.text()) != 0:
            self.irrad_film_file = self.ui.lineEdit_3.text()
            self.ui.lineEdit_3.setDisabled(True)

    def get_empty_field_file(self):
        self.ui.lineEdit_2.setText(self.search_file())

        if len(self.ui.lineEdit_2.text()) != 0:
            self.empty_field_file = self.ui.lineEdit_2.text()
            self.ui.lineEdit_2.setDisabled(True)

    def insert_tiff_file(self):
        img = QtGui.QPixmap(self.irrad_film_file)
        self.pixmap.setPixmap(img)

    def test(self):
        print('test connect')

    def get_dialog_window(self):
        self.form = Form()
        self.form.create_widgets_second_open()
        self.insert_data_in_fields()
        # self.form.openDialog.connect(self.test)
        self.form.show()

    def insert_data_in_fields(self):
        widgets = [self.form.gridLayout_3.itemAt(i).widget() for i in range(self.form.gridLayout_3.count())]
        lineedits = [i for i in widgets if isinstance(i, QLineEdit)]
        spinboxes = [i for i in widgets if isinstance(i, QDoubleSpinBox)]

        for path, dose, line, spin in zip(DosesAndPaths.paths, DosesAndPaths.doses, lineedits, spinboxes):
            if isinstance(line, QLineEdit):
                line.setText(path)
            if isinstance(spin, QDoubleSpinBox):
                spin.setValue((float(dose)))

        self.form.spinBox.setValue(DosesAndPaths.sigma)

    def search_file(self):
        """Поиск файла"""
        file_name = QFileDialog.getOpenFileName(self, 'Открыть файл', '', '*.tif', None, QFileDialog.DontUseNativeDialog)[0]
        return file_name

    def start_calc(self):
        calc = Dose(self.empty_field_file, DosesAndPaths.paths, DosesAndPaths.doses, self.irrad_film_file, DosesAndPaths.sigma)
        calc.red_chanel_calc()
        calc.calculate_calibrate_film()
        #calc.draw_curve()
        calc.draw_dose_map()
        self.insert_tiff_file()


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
