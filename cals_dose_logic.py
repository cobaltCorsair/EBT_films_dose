# Python 3.7
# -*- coding: utf-8 -*-
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas
import tifffile as tifimage
import matplotlib.widgets
from PyQt5.QtCore import pyqtSignal, QThread
from scipy.optimize import curve_fit
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QDoubleSpinBox, QMessageBox, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import RectangleSelector
from Dose import Ui_MainWindow
from calibrate_list import Ui_Form
from Axes import Ui_Form as Axes_form
from Curve import Ui_Form as Curve_form
from Values import Ui_Form as Values_form
from DB_and_settings import Ui_Form as DB_form
from database import db_connection
from database import dbProxy as db
from logicParser import LogicODVariant, LogicCurveVariants, LogicCurveFitsVariant, LogicParser
from filters import Filters

plt.switch_backend('agg')


class GraphicsPlotting:
    @staticmethod
    def draw_dose_map(z):
        """
        This method draws a map of dose distribution
        """
        application.figure_map.clf()
        ax = application.figure_map.add_subplot(111)
        application.cursor = matplotlib.widgets.Cursor(ax, useblit=False, color='red', linewidth=1)
        application.canvas_map.mpl_connect('button_press_event', lambda event: application.onclick(event, ax))
        application.canvas_map.draw()

        if DosesAndPaths.vmax is not None and DosesAndPaths.vmin is not None:
            im3 = ax.imshow(z, cmap="jet", vmin=DosesAndPaths.vmin, vmax=DosesAndPaths.vmax)
        else:
            im3 = ax.imshow(z, cmap="jet")

        formatter = lambda x, pos: round(x * DosesAndPaths.basis_formatter, 0)  # the resolution
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        application.figure_map.colorbar(im3, ax=ax, orientation="vertical")
        application.canvas_map.draw()

    @staticmethod
    def draw_curve(func, calculation_doses, setting_doses, p_opt, figure_graph, canvas_graph, sigma):
        """
        This method draws dose curve
        """
        figure_graph.clf()
        ax = figure_graph.add_subplot(111)
        ax.errorbar(calculation_doses, setting_doses, yerr=np.array(setting_doses[0:]) * (sigma / 100), fmt='ro',
                    label="Data points", markersize=6, capsize=5)
        ax.plot(calculation_doses, func(calculation_doses, *p_opt), label="Fit function", color="black", linestyle="-.")
        ax.grid(True, linestyle="-.")
        ax.legend(loc="best")
        ax.set_ylabel('Absorbed dose, Gy')
        ax.set_xlabel('Relative optical density')
        ax.set_xlim(0, np.max(calculation_doses) + 0.015)
        ax.set_ylim(0, np.max(setting_doses) + 0.5)
        canvas_graph.draw()

    @staticmethod
    def draw_curve_from_db(doses, ods, dose_object, figure_graph, canvas_graph):
        figure_graph.clf()
        ax = figure_graph.add_subplot(111)
        ax.plot(ods, dose_object.evaluateOD(ods), '*', label="Data points", color="red")
        ax.plot(np.linspace(ods[0], ods[-1], 500), dose_object.evaluateOD(np.linspace(ods[0], ods[-1], 500)),
                label="Fit function", color="black")
        ax.grid(True, linestyle="-.")
        ax.legend(loc="best")
        ax.set_ylabel('Absorbed dose, Gy')
        ax.set_xlabel('Relative optical density')
        canvas_graph.draw()


class Dose(QThread):
    """
    Calculate dose
    """
    progressChanged = QtCore.pyqtSignal(int)

    def __init__(self, zero_dose, zero_dose_for_irrad_film, calibrate_list, doses_list, irradiation_film, sigma,
                 func_name):
        super().__init__()
        self.zero_dose = zero_dose
        self.zero_dose_for_irrad_film = zero_dose_for_irrad_film
        self.calibrate_list = calibrate_list
        self.irradiation_film = irradiation_film
        self.setting_doses = doses_list
        self.sigma = sigma
        self.func_name = func_name

    def run(self):
        """
        Start thread
        """
        self.red_channel_calc()
        self.calculate_calibrate_film()
        self.calc_dose_map()

    @staticmethod
    def fit_func(func_name):
        """
        Returns the static method defining the approximation function
        :param func_name: method name
        """
        functions = {
            'base fit_func': Dose.fit_func1,
            'fit_func_pol2': Dose.fit_func_pol2,
            'fit_func_pol3': Dose.fit_func_pol3,
            'fit_func_pol5': Dose.fit_func_pol5
        }
        if func_name in functions:
            return functions[func_name]

    @staticmethod
    def fit_func1(od, a, b, c):
        """
        Fitting function for calibration curve
        :param od:
        :param a:
        :param b:
        :param c:
        :return:
        """
        return (b / (od - a)) + c

    @staticmethod
    def fit_func_pol2(od, x2, x1, x0):
        '''
        Fit with x2*od**2+x1*od+x0
        '''
        func = np.poly1d([x2, x1, x0])
        return func(od)

    @staticmethod
    def fit_func_pol3(od, x3, x2, x1, x0):
        '''
        Fit with x3*od**3+x2*od**2+x1*od+x0
        '''
        func = np.poly1d([x3, x2, x1, x0])
        return func(od)

    @staticmethod
    def fit_func_pol5(od, x5, x4, x3, x2, x1, x0):
        '''
        Fit with x5*od**5+x4*od**4+x3*od**3+x2*od**2+x1*od+x0
        '''
        func = np.poly1d([x5, x4, x3, x2, x1, x0])
        return func(od)

    @staticmethod
    def get_imarray(img):
        im = tifimage.imread(img)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        return imarray

    def red_channel_calc(self):
        """
        Calculate value in red channel of blank field
        :return: od_blank
        """
        blank_field_path = self.zero_dose
        od_blank = np.mean(Dose.get_imarray(blank_field_path))
        print("Blank field value: ", round(od_blank, 2))

        DosesAndPaths.red_channel_blank = od_blank
        return od_blank

    def calc_dose(self, path_to_film):
        """
        Image file processor
        """
        red_channel_current_tiff = np.mean(Dose.get_imarray(path_to_film))
        od_current_dose = np.log10(DosesAndPaths.red_channel_blank / red_channel_current_tiff)

        return od_current_dose

    def find_best_fit(self, path_to_film):
        """
        Finding best fit dose and writes it to the list
        """
        od_current_dose = self.calc_dose(path_to_film) - self.zero_dose
        DosesAndPaths.calculation_doses.append(od_current_dose)

    def calculate_calibrate_film(self):
        """
        Calculating dose for each file
        """
        # сначала считаем нулевую дозу
        self.zero_dose = self.calc_dose(list(self.calibrate_list)[0])
        # затем считаем для каждого файла с использованием посчитанной нулевой
        for i in self.calibrate_list:
            self.find_best_fit(i)
        try:
            p_opt, p_cov = curve_fit(self.fit_func(self.func_name), np.array(DosesAndPaths.calculation_doses[1:]),
                                     np.array(self.setting_doses[1:]),
                                     sigma=np.array(self.setting_doses[1:]) * (self.sigma / 100))
            DosesAndPaths.p_opt = p_opt
        except (ValueError, RuntimeError):

            print('Incorrect sigma value')

    def calc_dose_map(self):
        """
        Working with user image
        """
        try:
            zero_dose_for_irrad_film = self.calc_dose(self.zero_dose_for_irrad_film)
            print("\nShape of scanned film:", np.shape(CalcUI.choose_orig_or_crop()))
            progress = 0
            counter = 0
            print("\nPrepearing your file:\n")
            for i in np.nditer(CalcUI.choose_orig_or_crop()):
                x = np.log10(DosesAndPaths.red_channel_blank / i)
                x = x - zero_dose_for_irrad_film
                x = self.fit_func(self.func_name)(x, *DosesAndPaths.p_opt)
                DosesAndPaths.z = np.append(DosesAndPaths.z, x)

                counter = counter + 1
                if counter % 10000 == 0:
                    print("Iteration ", counter, "/", np.size(CalcUI.choose_orig_or_crop()))
                    progress += 1
                    self.progressChanged.emit(round(progress))

            DosesAndPaths.z = DosesAndPaths.z.reshape(np.shape(CalcUI.choose_orig_or_crop()))
            print("\nDose calculation ended!!!\n")
            self.progressChanged.emit(100)
            GraphicsPlotting().draw_dose_map(DosesAndPaths.z)
        except ValueError:
            print('No files found')


class DosesAndPaths:
    """
    Data-class
    """
    empty_field_file = None
    empty_scanner_field_file = None
    irrad_film_file = None
    calculation_doses = list()
    red_channel_blank = None
    p_opt = None
    doses = list()
    paths = list()
    sigma = 0
    z = list()
    basis_formatter = 0.17
    curve_object = None
    zero_from_db = None
    vmin = None
    vmax = None
    fit_func_type = None
    irrad_film_array = None
    irrad_film_array_original = None


class Form(QtWidgets.QWidget, Ui_Form):
    """
    UI class for displaying dose/path list
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.widget_count = 0
        self.all_widgets = None
        self.curve_win = None
        self.value_win = None

        self.pushButton_5.setDisabled(True)
        self.pushButton_9.setDisabled(True)

        self.pushButton.clicked.connect(lambda: self.get_empty_field_file(self.lineEdit))
        self.pushButton_2.clicked.connect(self.dynamic_add_fields)
        self.pushButton_3.clicked.connect(self.dynamic_delete_fields)
        self.pushButton_4.clicked.connect(self.get_all_params_widgets)
        self.pushButton_5.clicked.connect(self.draw_curve)
        self.pushButton_8.clicked.connect(SaveLoadData.create_json)
        self.pushButton_6.clicked.connect(lambda: self.get_empty_field_file(self.lineEdit_2))
        self.pushButton_9.clicked.connect(self.get_values)

    def search_file(self):
        """
        Search file
        """
        file_name = \
            QFileDialog.getOpenFileName(self, 'Open file', '', '*.tif', None, QFileDialog.DontUseNativeDialog)[0]
        return file_name

    def get_empty_field_file(self, line):
        """Set the found file in lineEdit"""
        line.setText(self.search_file())

        if len(line.text()) != 0:
            line.setDisabled(True)

    def dynamic_add_fields(self):
        """
        Dynamically adding fields to record new paths/doses
        """
        spin_box = QtWidgets.QDoubleSpinBox()
        qline_edit = QtWidgets.QLineEdit()
        push_button = QtWidgets.QPushButton("Select")
        checkbox = QtWidgets.QCheckBox()

        self.gridLayout_3.addWidget(checkbox)
        self.gridLayout_3.addWidget(spin_box)
        self.gridLayout_3.addWidget(qline_edit)
        self.gridLayout_3.addWidget(push_button)

        push_button.clicked.connect(lambda: self.get_empty_field_file(qline_edit))

        self.widget_count += 1
        self.adjustSize()

    def dynamic_delete_fields(self):
        """
        Deleting fields to record paths/doses
        """
        widgets = [self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count())]
        checkboxes = [i for i in widgets if isinstance(i, QCheckBox)]

        for k in checkboxes:
            if k.checkState() == 2:
                index = widgets.index(k)
                for j in range(4):
                    my_widget = self.gridLayout_3.itemAt(index).widget()
                    my_widget.setParent(None)
                    self.adjustSize()
                    widgets.remove(my_widget)

    def get_all_params_widgets(self):
        """
        Set values from fields to variables
        """
        doses = []
        paths = []
        sigma = self.spinBox.value()
        widgets = (self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count()))
        self.all_widgets = widgets
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                paths.append(widget.text())
            if isinstance(widget, QDoubleSpinBox):
                doses.append(widget.value())
            if isinstance(widget, QLineEdit) and widget.text() is '':
                Warnings.error_empty_value()

        DosesAndPaths.doses = doses
        DosesAndPaths.paths = paths
        DosesAndPaths.sigma = sigma
        DosesAndPaths.fit_func_type = self.comboBox.currentText()
        DosesAndPaths.empty_scanner_field_file = self.lineEdit_2.text()
        DosesAndPaths.calculation_doses.clear()

        self.get_enabled_curve_drawing()
        CalcUI.HAND_SWITCH_MODE = True

    def get_enabled_curve_drawing(self):
        """
        Blocking the availability of fields for editing
        """
        if len(DosesAndPaths.doses) is not 0 and len(DosesAndPaths.paths) is not 0:
            self.pushButton_5.setDisabled(False)

    def draw_curve(self):
        """
        The method connects methods of drawing graphs
        """
        self.curve_win = CurveWindow()
        self.curve_win.get_curve()
        self.curve_win.setMinimumSize(640, 480)
        self.curve_win.show()
        self.pushButton_5.setDisabled(True)
        self.pushButton_9.setDisabled(False)

    def create_widgets_second_open(self):
        """
        The method restores the fields created by the user when the window is reopened
        """
        data_count = len(DosesAndPaths.doses)
        if self.gridLayout_3.count() >= 6 and data_count > 1:
            for i in range(data_count - 1):
                self.dynamic_add_fields()

    def insert_data_in_fields(self):
        """
        Fill in the dialog window with doses and paths when opening
        """
        widgets = [self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count())]
        lineedits = [i for i in widgets if isinstance(i, QLineEdit)]
        spinboxes = [i for i in widgets if isinstance(i, QDoubleSpinBox)]

        for path, dose, line, spin in zip(DosesAndPaths.paths, DosesAndPaths.doses, lineedits, spinboxes):
            if isinstance(line, QLineEdit):
                line.setText(path)
            if isinstance(spin, QDoubleSpinBox):
                spin.setValue((float(dose)))

        self.spinBox.setValue(DosesAndPaths.sigma)
        self.lineEdit_2.setText(DosesAndPaths.empty_scanner_field_file)
        self.comboBox.setCurrentText(DosesAndPaths.fit_func_type)

    def get_values(self):
        """
        Get the values of doses, calculation doses and p_opt in dialog window
        """
        self.value_win = ValuesWindow()
        if len(DosesAndPaths.calculation_doses) > 0:
            self.value_win.plainTextEdit.appendPlainText(
                ('DOSES: \n' + ('\n'.join(map(str, [round(x, 4) for x in DosesAndPaths.doses]))).replace('.', ',')))
            self.value_win.plainTextEdit.appendPlainText(('\nOPTICAL DENSITY: \n' + (
                '\n'.join(map(str, [round(x, 4) for x in DosesAndPaths.calculation_doses]))).replace('.', ',')))
            self.value_win.plainTextEdit.appendPlainText(('\nPOLY_COEF_A_B_C: \n' + (
                '\n'.join(map(str, [round(x, 4) for x in DosesAndPaths.p_opt]))).replace('.', ',')))
        self.value_win.show()


class ValuesWindow(QtWidgets.QWidget, Values_form):
    """
    Class of the dialog window with a values
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)


class CurveWindow(QtWidgets.QWidget, Curve_form):
    """
    Class of the dialog window with a curve
    """
    closeDialog = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.figure_graph = plt.figure()
        self.canvas_graph = FigureCanvas(self.figure_graph)
        self.toolbar_graph = NavigationToolbar(self.canvas_graph, self)
        self.verticalLayout_5.addWidget(self.toolbar_graph)
        self.verticalLayout_7.addWidget(self.canvas_graph)

    def get_curve(self):
        """
        Draw dose curve
        """
        try:
            calc = Dose(DosesAndPaths.empty_scanner_field_file, DosesAndPaths.empty_field_file, DosesAndPaths.paths,
                        DosesAndPaths.doses,
                        DosesAndPaths.irrad_film_file, DosesAndPaths.sigma, DosesAndPaths.fit_func_type)
            calc.red_channel_calc()
            calc.calculate_calibrate_film()
            GraphicsPlotting.draw_curve(Dose.fit_func(DosesAndPaths.fit_func_type), DosesAndPaths.calculation_doses,
                                        DosesAndPaths.doses, DosesAndPaths.p_opt, self.figure_graph, self.canvas_graph,
                                        DosesAndPaths.sigma)
        except (ValueError, TypeError):
            print('Incorrect parameters')

    def get_curve_from_db_data(self, doses, ods, evaluate_od):
        """
        Draw dose curve from db data
        """
        try:
            GraphicsPlotting.draw_curve_from_db(doses[1:], ods[1:], evaluate_od, self.figure_graph, self.canvas_graph)
        except Exception as e:
            Warnings.error_incorrect_value()
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)

    def closeEvent(self, event):
        """
        Clear figure
        :param event: Window close
        """
        plt.close(self.figure_graph)
        self.closeDialog.emit()


class AxesWindow(QtWidgets.QWidget, Axes_form):
    """
    Class for drawing graphs on the X and Y axes
    """
    closeDialog = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.value_win = None

        self.figure_map_x = plt.figure()
        self.canvas_map_x = FigureCanvas(self.figure_map_x)
        self.verticalLayout.addWidget(self.canvas_map_x)
        self.toolbar_x = NavigationToolbar(self.canvas_map_x, self)
        self.verticalLayout_4.addWidget(self.toolbar_x)

        self.figure_map_y = plt.figure()
        self.canvas_map_y = FigureCanvas(self.figure_map_y)
        self.verticalLayout_3.addWidget(self.canvas_map_y)
        self.toolbar_y = NavigationToolbar(self.canvas_map_y, self)
        self.verticalLayout_5.addWidget(self.toolbar_y)

    @staticmethod
    def dose_limits_for_graph(slice, ax):
        """
        Limits the dose if a checkbox was checked
        :param slice: axis segment
        :param ax: сanvas
        :return: slice
        """
        if DosesAndPaths.vmax is not None and DosesAndPaths.vmin is not None:
            slice_clipped = np.clip(slice, DosesAndPaths.vmin, DosesAndPaths.vmax)
            ax.plot(slice_clipped)
            return slice_clipped
        else:
            ax.plot(slice)
            return slice

    def draw_graphics(self, slice_x, slice_y):
        """
        Method for graphing the X and Y axes
        :param slice_x: Set of values along the X-axis
        :param slice_y: Set of values along the Y-axis
        """
        formatter = lambda x, pos: round(x * DosesAndPaths.basis_formatter, 0)  # the resolution

        # x axis
        self.figure_map_x.clf()
        ax_x = self.figure_map_x.add_subplot(111)
        ax_x.grid(True, linestyle="-.")
        slice_values_x = AxesWindow.dose_limits_for_graph(slice_x, ax_x)
        ax_x.xaxis.set_major_formatter(formatter)
        ax_x.set_xlabel('mm')
        ax_x.set_ylabel('Absorbed dose, Gy')
        self.canvas_map_x.draw()
        self.pushButton.clicked.connect(lambda: self.get_values(slice_values_x, 'X axis'))

        # y axis
        self.figure_map_y.clf()
        ax_y = self.figure_map_y.add_subplot(111)
        ax_y.grid(True, linestyle="-.")
        slice_values_y = AxesWindow.dose_limits_for_graph(slice_y, ax_y)
        ax_y.xaxis.set_major_formatter(formatter)
        ax_y.set_xlabel('mm')
        ax_y.set_ylabel('Absorbed dose, Gy')
        self.canvas_map_y.draw()
        self.pushButton_3.clicked.connect(lambda: self.get_values(slice_values_y, 'Y axis'))

    def get_values(self, values, ax_name):
        """
        Get the values of doses on the axis in dialog window
        :param values: values of doses
        :param ax_name: name of the axis
        """
        self.value_win = ValuesWindow()
        self.value_win.label.setText(ax_name)
        values_with_separator = ('\n'.join(map(str, [round(x, 4) for x in values]))).replace('.', ',')
        if len(values) > 0:
            self.value_win.plainTextEdit.appendPlainText(values_with_separator)
        self.value_win.show()

    def closeEvent(self, event):
        """
        Clear figure
        :param event: Window close
        """
        plt.close(self.figure_map_x)
        plt.close(self.figure_map_y)
        self.closeDialog.emit()


class CalcUI(QtWidgets.QMainWindow):
    """
    Main interface
    """
    # connect to the database
    connect = False
    try:
        collection = db_connection.Connect.start()
        connect = True
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)

    HAND_SWITCH_MODE = True

    def __init__(self, *args, **kwargs):
        super(CalcUI, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.form = None
        self.bd_win = None
        self.graphic_dialog = None
        self.thread = None
        self.RS = None
        self.pic_ax = None
        self.start_pos = None
        self.end_pos = None

        self.image_map = plt.figure()
        self.image_canvas = FigureCanvas(self.image_map)
        self.image_toolbar = NavigationToolbar(self.image_canvas, self)
        self.ui.verticalLayout.addWidget(self.image_toolbar)
        self.ui.verticalLayout.addWidget(self.image_canvas)

        self.figure_map = plt.figure()
        self.canvas_map = FigureCanvas(self.figure_map)
        self.toolbar_map = NavigationToolbar(self.canvas_map, self)
        self.ui.verticalLayout_2.addWidget(self.toolbar_map)
        self.ui.verticalLayout_2.addWidget(self.canvas_map)
        self.ui.comboBox.addItems(self.get_filters)

        self.ax = self.figure_map.add_subplot(111)
        # Set cursor
        self.cursor = None

        self.ui.pushButton_7.clicked.connect(self.get_irrad_film_file)
        self.ui.pushButton.clicked.connect(self.get_empty_field_file)
        self.ui.pushButton_8.clicked.connect(self.get_dialog_window)
        self.ui.pushButton_4.clicked.connect(self.start_calc)
        self.ui.pushButton_9.clicked.connect(SaveLoadData.load_json)
        self.ui.pushButton_2.clicked.connect(self.get_db_and_setting_window)
        self.ui.pushButton_3.clicked.connect(self.cropping_by_button)
        self.ui.pushButton_5.clicked.connect(SaveLoadData.save_as_excel_file)

        self.ui.pushButton_2.setDisabled(True)
        if CalcUI.connect:
            self.ui.pushButton_2.setDisabled(False)

    def get_irrad_film_file(self):
        """
        Find and paste the irradiate film file in tiff format
        """
        DosesAndPaths.irrad_film_array_original = None
        DosesAndPaths.irrad_film_array = None

        self.ui.lineEdit_3.setText(self.search_file('*.tif'))

        if len(self.ui.lineEdit_3.text()) != 0:
            DosesAndPaths.irrad_film_file = self.ui.lineEdit_3.text()
            DosesAndPaths.irrad_film_array_original = Dose.get_imarray(DosesAndPaths.irrad_film_file)
            self.ui.lineEdit_3.setDisabled(True)
            self.insert_tiff_file()
        else:
            DosesAndPaths.irrad_film_file = None
            self.image_map.clf()
            self.image_canvas.draw_idle()

    def get_empty_field_file(self):
        """
        Find and paste the empty file in tiff format
        """
        self.ui.lineEdit.setText(self.search_file('*.tif'))

        if len(self.ui.lineEdit.text()) != 0:
            DosesAndPaths.empty_field_file = self.ui.lineEdit.text()
            self.ui.lineEdit.setDisabled(True)

    def get_dpi_value(self):
        """
        Set DPI value in variable
        """
        DosesAndPaths.basis_formatter = 25.4 / self.ui.spinBox.value()

    def get_vmin_vmax_values(self):
        """
        Set vmin/vmax value in z_map
        """
        # Reset the values to None at first
        DosesAndPaths.vmin = None
        DosesAndPaths.vmax = None

        vmin = self.ui.doubleSpinBox.value()
        vmax = self.ui.doubleSpinBox_2.value()

        if self.ui.checkBox_2.isChecked():
            DosesAndPaths.vmin = vmin
            DosesAndPaths.vmax = vmax

    def insert_tiff_file(self):
        """
        Insert a picture of the film in the interface window
        """
        formatter = lambda x, pos: round(x * DosesAndPaths.basis_formatter, 0)  # the resolution

        self.image_map.clf()
        img = plt.imread(DosesAndPaths.irrad_film_file)
        ax = self.image_map.add_subplot(111)
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        ax.imshow(img)

        self.pic_ax = ax

        self.RS = RectangleSelector(ax, self.line_select_callback,
                                    drawtype='box', useblit=False, button=[1],
                                    minspanx=5, minspany=5, spancoords='pixels',
                                    interactive=True)

        self.image_canvas.draw()

    def line_select_callback(self, eclick, erelease):
        '''
        :param eclick: matplotlib event at press
        :param erelease: matplotlib event at release
        :return:
        '''
        print(' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata))
        print(' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata))
        print(' used button   : ', eclick.button)

        self.start_pos = [eclick.xdata, eclick.ydata]
        self.end_pos = [erelease.xdata, erelease.ydata]

        center = self.RS.center  # xy coord, units same as plot axes
        extents = self.RS.extents  # Return (xmin, xmax, ymin, ymax)

    @staticmethod
    def crop(xmin, xmax, ymin, ymax):
        """
        Return the cropped image at the xmin, xmax, ymin, ymax coordinates
        """
        image = DosesAndPaths.irrad_film_array_original

        if xmax == -1:
            xmax = image.shape[1] - 1
        if ymax == -1:
            ymax = image.shape[0] - 1

        mask = np.zeros(image.shape)
        mask[ymin:ymax + 1, xmin:xmax + 1] = 1
        m = mask > 0

        DosesAndPaths.irrad_film_array = image[m].reshape((ymax + 1 - ymin, xmax + 1 - xmin))
        return image[m].reshape((ymax + 1 - ymin, xmax + 1 - xmin))

    def get_crop(self, ax, xmin, xmax, ymin, ymax):
        """
        Get cropped image
        :param ax: ax object
        :param xmin:
        :param xmax:
        :param ymin:
        :param ymax:
        :return:
        """
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.invert_yaxis()
        self.RS.set_visible(False)
        self.image_canvas.draw_idle()
        # crop image
        CalcUI.crop(int(xmin), int(xmax), int(ymin), int(ymax))

    def cropping_by_button(self):
        """
        This method crops the image at the click of a button
        :return:
        """
        if self.pic_ax and self.RS.extents and \
                self.start_pos is not None and self.end_pos is not None and \
                self.start_pos[0] != self.end_pos[0]:
            self.get_crop(self.pic_ax, *self.RS.extents)
        else:
            Warnings.inform_about_area()

        self.start_pos = None
        self.end_pos = None

    def onclick(self, event, ax):
        """
        Place the cross cursor on the dose map
        :param event: onclick event
        ::param ax: existing dose map
        """
        state = self.toolbar_map.mode
        if event.inaxes == ax and len(DosesAndPaths.z) > 1 and state == '':
            try:
                self.cursor.onmove(event)
                x, y = int(event.xdata), int(event.ydata)
                slice_y = DosesAndPaths.z[:, x]
                slice_x = DosesAndPaths.z[y, :]

                self.graphic_dialog = AxesWindow()
                self.graphic_dialog.draw_graphics(slice_x, slice_y)
                self.graphic_dialog.setMinimumSize(640, 480)
                self.graphic_dialog.show()
            except IndexError:
                print('Too many indices for array')

    @property
    def get_filters(self):
        """Get filters variant"""
        filters = [i.name for i in Filters]
        return filters

    def select_filter(self):
        """For test"""
        print(self.ui.comboBox.currentText(), Filters.__dict__[self.ui.comboBox.currentText()])

    def get_dialog_window(self):
        """
        Show dialog window with doses and paths
        """
        self.form = Form()
        self.form.create_widgets_second_open()
        self.form.insert_data_in_fields()
        self.form.show()

    def search_file(self, file_type):
        """
        Search file any type
        :param file_type: type of file
        """
        file_name = \
            QFileDialog.getOpenFileName(self, 'Open file', '', file_type, None, QFileDialog.DontUseNativeDialog)[0]
        return file_name

    def progress_bar_update(self, data):
        """
        Updating progress bar
        """
        self.ui.progressBar.setValue(data)

    def first_film_from_calibration(self):
        """
        Defining the first file from the calibration as unexposed
        :return:
        """
        if self.ui.checkBox.isChecked() and CalcUI.HAND_SWITCH_MODE:
            try:
                DosesAndPaths.empty_field_file = DosesAndPaths.paths[0]
            except (TypeError, IndexError):
                Warnings.error_confirm_calibration()

        elif self.ui.checkBox.isChecked() and not CalcUI.HAND_SWITCH_MODE:
            DosesAndPaths.empty_field_file = DosesAndPaths.zero_from_db
        elif not self.ui.checkBox.isChecked() and len(self.ui.lineEdit.text()) is not 0:
            DosesAndPaths.empty_field_file = self.ui.lineEdit.text()
        else:
            Warnings.error_empty_film()

    def start_calc(self):
        """
        Running the calculation in the thread
        """
        self.first_film_from_calibration()
        self.get_vmin_vmax_values()

        if self.check_fields_manual_mode() and CalcUI.HAND_SWITCH_MODE:
            # manual mode
            self.calc_from_manual()

        if self.check_fields_bd_mode() and not CalcUI.HAND_SWITCH_MODE:
            # db mode
            if self.ui.checkBox.isChecked():
                empty_file = DosesAndPaths.zero_from_db
            elif len(self.ui.lineEdit.text()) is not 0:
                empty_file = LogicParser.getMean4FilmByFilename(DosesAndPaths.empty_field_file)
            else:
                Warnings.error_empty_film()
                return False

            try:
                self.calc_from_db(empty_file)
            except ValueError:
                Warnings.error_incorrect_value()

        # Todo: убрать вывод названия фильтра по кнопке "Calc" после имплементации ф-ции
        self.select_filter()

    def calc_from_manual(self):
        """
        Calculate from manual mode
        """
        self.get_dpi_value()
        DosesAndPaths.z = list()
        self.thread = Dose(DosesAndPaths.empty_scanner_field_file, DosesAndPaths.empty_field_file,
                           DosesAndPaths.paths, DosesAndPaths.doses,
                           DosesAndPaths.irrad_film_file,
                           DosesAndPaths.sigma, DosesAndPaths.fit_func_type)
        self.thread.start()
        self.thread.progressChanged.connect(self.progress_bar_update)

    @staticmethod
    def choose_orig_or_crop():
        """
        Select the variable to be passed to the function depending on its state
        :return: DosesAndPaths.irrad_film_array or DosesAndPaths.irrad_film_array
        """
        if DosesAndPaths.irrad_film_array is not None and DosesAndPaths.irrad_film_array_original is not None:
            return DosesAndPaths.irrad_film_array
        if DosesAndPaths.irrad_film_array is None and DosesAndPaths.irrad_film_array_original is not None:
            return DosesAndPaths.irrad_film_array_original
        if DosesAndPaths.irrad_film_array is not None and DosesAndPaths.irrad_film_array_original is None:
            return DosesAndPaths.irrad_film_array

    def calc_from_db(self, empty_file):
        """
        Perform calculations from the database usage mode
        :param empty_file: Value of the empty file loaded from the database
        :return:
        """
        self.get_dpi_value()
        DosesAndPaths.z = list()
        im_arr_first = CalcUI.choose_orig_or_crop()
        im_arr_flatt = im_arr_first.flatten()
        parsed_empty_file = empty_file
        z_object = DosesAndPaths.curve_object.preparePixValue(im_arr_flatt, parsed_empty_file)
        DosesAndPaths.z = (DosesAndPaths.curve_object.evaluateOD(z_object)).reshape(im_arr_first.shape)
        GraphicsPlotting.draw_dose_map(DosesAndPaths.z)
        self.progress_bar_update(100)

    def get_db_and_setting_window(self):
        """
        Show dialog window with db and settings
        """
        self.bd_win = DatabaseAndSettings()
        self.bd_win.show()

    @staticmethod
    def check_fields_manual_mode():
        """
        Check fields for validity
        """
        if DosesAndPaths.empty_scanner_field_file is not None and DosesAndPaths.empty_field_file is not None \
                and DosesAndPaths.irrad_film_file is not None and len(DosesAndPaths.paths) > 0 \
                and len(DosesAndPaths.doses) > 0 and DosesAndPaths.basis_formatter > 0:
            return True

    @staticmethod
    def check_fields_bd_mode():
        if DosesAndPaths.curve_object is not None and DosesAndPaths.irrad_film_file is not None \
                and DosesAndPaths.empty_field_file is not None and DosesAndPaths.irrad_film_array_original is not None:
            return True


class Warnings:
    """
    This class contains pop-up errors
    """

    @staticmethod
    def error_exist_files(file) -> list:
        """
        :param file: list only
        :return:
        """
        QMessageBox.critical(None, "Error", "<b>No such file or directory</b><br><br>"
                                            f"Some selected files are not on the disk. List of files:<br>"
                                            f"{'<br>'.join(file)}", QMessageBox.Ok)

    @staticmethod
    def error_special_symbols():
        QMessageBox.critical(None, "Error ", "<b>Incorrect name</b><br><br>"
                                             "Please re-save the file using the correct name without special "
                                             "characters",
                             QMessageBox.Ok)

    @staticmethod
    def error_incorrect_value():
        QMessageBox.critical(None, "Error", "<b>Incorrect value</b><br><br>"
                                            "Please select a different fitting function",
                             QMessageBox.Ok)

    @staticmethod
    def error_empty_value():
        QMessageBox.critical(None, "Error", "<b>Empty value</b><br><br>"
                                            "Check the fields with film paths for emptiness",
                             QMessageBox.Ok)
        return False

    @staticmethod
    def inform_about_area():
        QMessageBox.information(None, "Information", "<b>Before cutting the film</b><br>"
                                                     "need to allocate an area for trimming",
                                QMessageBox.Ok)

    @staticmethod
    def error_confirm_calibration():
        QMessageBox.critical(None, "Error", "<b>Empty value</b><br><br>"
                                            "Need to confirm use of calibration",
                             QMessageBox.Ok)
        return False

    @staticmethod
    def error_empty_film():
        QMessageBox.critical(None, "Error", "<b>Empty value</b><br><br>"
                                            "Need to select a blank film or use the first file",
                             QMessageBox.Ok)

    @staticmethod
    def error_empty_dose():
        QMessageBox.critical(None, "Data error", "<b>No data</b><br><br>"
                                            "Need to calculate dose before outputting to file",
                             QMessageBox.Ok)


class SaveLoadData:
    """
    Сlass for save and load json
    """
    db_win_setting = None

    @staticmethod
    def create_json():
        """
        Create json object
        """
        data = {'calibrate_list': []}
        if len(DosesAndPaths.doses) > 0 and len(DosesAndPaths.paths) > 0:
            dose_path_data = dict(zip(DosesAndPaths.doses, DosesAndPaths.paths))
            data['calibrate_list'].append(dose_path_data)
        if DosesAndPaths.sigma is not 0:
            data['sigma'] = DosesAndPaths.sigma
        if DosesAndPaths.empty_scanner_field_file is not None:
            data['empty_scanner_field_file'] = DosesAndPaths.empty_scanner_field_file

        SaveLoadData.save_json(data, 'calibrate_list')

    @staticmethod
    def save_json(data, file_name):
        """
        Save json file
        :param file_name: name of the file to be saved
        :param data: json object
        """
        filename, _ = QFileDialog.getSaveFileName(None, 'Save calibrate setting or list',
                                                  file_name + '.json',
                                                  'JSON files (*.json);;all files(*.*)',
                                                  options=QFileDialog.DontUseNativeDialog)
        if filename is not '':
            try:
                with open(filename, 'w', encoding='utf-8') as outfile:
                    json.dump(data, outfile, ensure_ascii=False, indent=4)
            except OSError:
                Warnings.error_special_symbols()

    @staticmethod
    def load_json():
        """
        Load and parse json file
        """
        data = application.search_file('*.json')
        not_exist_files = []

        if os.path.exists(data):
            with open(data, encoding='utf-8') as f:
                data = json.load(f)
                for p in data['calibrate_list']:
                    DosesAndPaths.doses = [float(i) for i in p.keys()]
                    DosesAndPaths.paths = p.values()

                DosesAndPaths.sigma = data['sigma']
                DosesAndPaths.empty_scanner_field_file = data['empty_scanner_field_file']

                Warnings().error_exist_files([data['empty_scanner_field_file']])

        for i in p.values():
            if not os.path.exists(i):
                not_exist_files.append(i)

        if not_exist_files:
            Warnings().error_exist_files(not_exist_files)

    @staticmethod
    def save_db_win_setting(facility, lot, hours, dose_limit, od, fit_func, fitting):
        SaveLoadData.db_win_setting = {
            'facility_name': facility,
            'lot_number': lot,
            'hours_after_irrad': hours,
            'dose_limit': dose_limit,
            'optical_density': od,
            'fit_funtion': fit_func,
            'curve_fitting': fitting
        }

    @staticmethod
    def load_json_settings():
        """
        Load and parse json file
        """
        data = application.search_file('*.json')

        if os.path.exists(data):
            with open(data, encoding='utf-8') as f:
                data = json.load(f)
                SaveLoadData.save_db_win_setting(data['facility_name'], data['lot_number'], data['hours_after_irrad'],
                                                 data['dose_limit'], data['optical_density'], data['fit_funtion'],
                                                 data['curve_fitting'])

    @staticmethod
    def save_as_excel_file():
        """
        Save xlsx file
        """
        if len(DosesAndPaths.z) > 0:
            dataframe_array = pandas.DataFrame(DosesAndPaths.z).T

            filename, _ = QFileDialog.getSaveFileName(None, 'Save calibrate setting or list', 'dose_data.xlsx',
                                                      'JSON files (*.xlsx);;all files(*.*)',
                                                      options=QFileDialog.DontUseNativeDialog)
            if filename is not '':
                try:
                    dataframe_array.to_excel(excel_writer=filename+'.xlsx')
                except OSError:
                    Warnings.error_special_symbols()
        else:
            Warnings.error_empty_dose()


class DatabaseAndSettings(QtWidgets.QWidget, DB_form):
    """Class contains a description of the settings window
    for loading data from the database,
    as well as the curve approximation settings"""

    closeDialog = pyqtSignal()
    openDialog = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.dose_curve_object = None

        self.curve_win = None
        self.value_win = None
        # filling the first combobox
        self.set_values_in_start_setting()
        # As soon as the value in the connect object changes, the set in the dependent list changes
        self.comboBox.currentIndexChanged.connect(self.set_secondary_values_in_comboboxes)
        self.comboBox_2.currentIndexChanged.connect(self.set_hours_values_in_comboboxes)
        self.comboBox_5.currentIndexChanged.connect(self.select_curve_fits_variant)
        self.pushButton_4.clicked.connect(self.get_approve)
        self.pushButton_5.clicked.connect(self.draw_curve_from_db_data)
        self.pushButton_9.clicked.connect(self.get_values)
        self.pushButton_4.clicked.connect(self.save_values)

        self.pushButton_5.setDisabled(True)
        self.pushButton_9.setDisabled(True)
        self.pushButton_2.setDisabled(True)

        self.pushButton_2.clicked.connect(self.save_json_settings)
        self.pushButton.clicked.connect(self.load_the_latest_settings)

    @staticmethod
    def get_database_facility_values():
        """Load all facilities from the database"""
        facilities = db.getListOfFacilities(CalcUI.collection)
        return facilities

    def get_database_available_facilities_EVT4(self):
        """Load the available facilities from the database"""
        facilities = db.getListOfAvailableEBT4Facility(CalcUI.collection, self.comboBox.currentText())
        return facilities

    def set_values_in_start_setting(self):
        """Filling the combo boxes on start (all)"""
        self.comboBox.addItems(DatabaseAndSettings.get_database_facility_values())
        self.comboBox_2.addItems(self.get_database_available_facilities_EVT4())
        self.comboBox_3.addItems(self.get_database_hours_after_irradiation())

        self.comboBox_4.addItems(self.get_od_variant)
        self.comboBox_5.addItems(self.get_curve_variant)
        self.comboBox_6.addItems(self.get_curve_fits_variant)

    def set_secondary_values_in_comboboxes(self):
        """Filling the second combo box (available facilities)"""
        self.comboBox_2.clear()
        self.comboBox_2.addItems(self.get_database_available_facilities_EVT4())

    def get_database_hours_after_irradiation(self):
        """Load the available facilities from the database"""
        hours = db.getListOfAvailableHoursAfterIrradiation4FacilityAndLotNo(CalcUI.collection,
                                                                            self.comboBox.currentText(),
                                                                            self.comboBox_2.currentText())
        return [str(item) for item in hours]

    def set_hours_values_in_comboboxes(self):
        """Filling the third combo box (hours after irradiation)"""
        self.comboBox_3.clear()
        self.comboBox_3.addItems(self.get_database_hours_after_irradiation())

    def load_the_latest_settings(self):
        """
        Load the settings from a file
        :return:
        """
        SaveLoadData.load_json_settings()
        self.reload_old_setting()

    def save_json_settings(self):
        """
        Save the settings to a file
        :return:
        """
        if SaveLoadData.db_win_setting:
            SaveLoadData.save_json(SaveLoadData.db_win_setting, 'bd_method_settings')

    def reload_old_setting(self):
        """
        Restore the saved settings when reopen the window
        :return:
        """
        if SaveLoadData.db_win_setting is not None:
            self.comboBox.setCurrentText(SaveLoadData.db_win_setting['facility_name'])
            self.comboBox_2.setCurrentText(SaveLoadData.db_win_setting['lot_number'])
            self.comboBox_3.setCurrentText(SaveLoadData.db_win_setting['hours_after_irrad'])
            self.doubleSpinBox.setValue(float(SaveLoadData.db_win_setting['dose_limit']))
            self.comboBox_4.setCurrentText(SaveLoadData.db_win_setting['optical_density'])
            self.comboBox_5.setCurrentText(SaveLoadData.db_win_setting['fit_funtion'])
            self.comboBox_6.setCurrentText(SaveLoadData.db_win_setting['curve_fitting'])

    @property
    def get_od_variant(self):
        """Select optical density variant"""
        optical_density = [i.name for i in LogicODVariant]
        return optical_density

    @property
    def get_curve_variant(self):
        """Select curve variant"""
        curves = [i.name for i in LogicCurveVariants]
        return curves

    @property
    def get_curve_fits_variant(self):
        """Select curve fit variant"""
        curve_fits = [i.name for i in LogicCurveFitsVariant]
        return curve_fits

    def select_curve_fits_variant(self):
        """Changes the function sets for different approximation types.
        (Implemented so far only for one type of function.)"""
        self.comboBox_6.clear()
        if self.comboBox_5.currentText() == 'useCurveFit':
            self.comboBox_6.addItems(self.get_curve_fits_variant)
        else:
            return []

    def database_query_methods(self, method):
        """
        :param method: Type of method used
        :return: query result in the database
        """
        if method == 'basic':
            return db.getData4CalibrationCurve(CalcUI.collection, self.comboBox.currentText(),
                                               self.comboBox_2.currentText(), int(self.comboBox_3.currentText()))
        elif method == 'zero_film':
            return db.getZeroFilmData4ExactLotNo(CalcUI.collection, self.comboBox.currentText(),
                                                 self.comboBox_2.currentText(), int(self.comboBox_3.currentText()))
        elif method == 'get_dict':
            return db.getDict4ExactCurveWithDoseLimit(CalcUI.collection, self.comboBox.currentText(),
                                                      self.comboBox_2.currentText(),
                                                      int(self.comboBox_3.currentText()), self.doubleSpinBox.value())

    def get_zero_film(self):
        """
        Get the first film from the calibration
        :return:
        """
        zero_from_db = db.getZeroFilmData4ExactLotNo(CalcUI.collection, self.comboBox.currentText(),
                                                     self.comboBox_2.currentText(),
                                                     int(self.comboBox_3.currentText()))

        DosesAndPaths.zero_from_db = zero_from_db['meanRedChannel']

    def get_approve(self):
        """
        Values when you press OK
        :return:
        """
        if len(self.comboBox_6.currentText()) is 0:
            # if not contains last argument
            curve_object = LogicParser(self.database_query_methods('get_dict'),
                                       LogicODVariant.__dict__[self.comboBox_4.currentText()],
                                       LogicCurveVariants.__dict__[self.comboBox_5.currentText()])
        else:
            # if contains last argument
            curve_object = LogicParser(self.database_query_methods('get_dict'),
                                       LogicODVariant.__dict__[self.comboBox_4.currentText()],
                                       LogicCurveVariants.__dict__[self.comboBox_5.currentText()],
                                       fitFunc=LogicCurveFitsVariant.__dict__[self.comboBox_6.currentText()])

        self.dose_curve_object = curve_object
        DosesAndPaths.curve_object = self.dose_curve_object

        self.pushButton_5.setDisabled(False)
        self.pushButton_9.setDisabled(False)
        self.pushButton_2.setDisabled(False)

        CalcUI.HAND_SWITCH_MODE = False
        self.get_zero_film()

    def draw_curve_from_db_data(self):
        """
        Drawing a curve
        :return:
        """
        self.curve_win = CurveWindow()
        self.curve_win.get_curve_from_db_data(self.dose_curve_object.calibDoses, self.dose_curve_object.calibOds,
                                              self.dose_curve_object)
        self.curve_win.setMinimumSize(640, 480)
        self.curve_win.show()

        self.pushButton_5.setDisabled(True)

    def get_values(self):
        """
        Get the values of doses, optical density in dialog window
        """
        self.value_win = ValuesWindow()
        try:
            if self.dose_curve_object is not None:
                self.value_win.plainTextEdit.appendPlainText(
                    ('DOSES: \n' + ('\n'.join(map(str, [round(x, 4) for x in self.dose_curve_object.evaluateOD(
                        self.dose_curve_object.calibOds
                    )]))).replace('.', ',')))
                self.value_win.plainTextEdit.appendPlainText(('\nOPTICAL DENSITY: \n' + (
                    '\n'.join(map(str, [round(x, 4) for x in self.dose_curve_object.calibOds]))).replace('.', ',')))
            self.value_win.show()
        except ValueError:
            Warnings.error_incorrect_value()

    def save_values(self):
        """
        Save settings from fields at json-liked format
        :return:
        """
        SaveLoadData.save_db_win_setting(self.comboBox.currentText(), self.comboBox_2.currentText(),
                                         self.comboBox_3.currentText(), self.doubleSpinBox.value(),
                                         self.comboBox_4.currentText(), self.comboBox_5.currentText(),
                                         self.comboBox_6.currentText())

    def closeEvent(self, event):
        """
        :param event: Window close
        """
        self.closeDialog.emit()

    def showEvent(self, event):
        """
        :param event: Window show
        """
        self.reload_old_setting()
        self.openDialog.emit()


app = QtWidgets.QApplication([])
# icon
# ico = QtGui.QIcon('./src/icon.png')
# app.setWindowIcon(ico)
# style GUI
app.setStyle("Fusion")
app.processEvents()
application = CalcUI()
# win title
application.setWindowTitle("Dose calculator")
# set minimum size
application.setMinimumSize(1200, 800)
application.show()
sys.exit(app.exec())
