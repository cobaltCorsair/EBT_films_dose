# Python 3.7
# -*- coding: utf-8 -*-
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
import tifffile as tifimage
import matplotlib.widgets
from PyQt5.QtCore import pyqtSignal, QThread
from scipy.optimize import curve_fit
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QDoubleSpinBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from Dose import Ui_MainWindow
from calibrate_list import Ui_Form
from Axes import Ui_Form as Axes_form
from Curve import Ui_Form as Curve_form
from Values import Ui_Form as Values_form

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
        im3 = ax.imshow(z, cmap="jet", vmin=0)
        formatter = lambda x, pos: round(x * DosesAndPaths.basis_formatter, 3)  # the resolution
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


class Dose(QThread):
    """
    Calculate dose
    """
    progressChanged = QtCore.pyqtSignal(int)

    def __init__(self, zero_dose, zero_dose_for_irrad_film, calibrate_list, doses_list, irradiation_film, sigma):
        super().__init__()
        self.zero_dose = zero_dose
        self.zero_dose_for_irrad_film = zero_dose_for_irrad_film
        self.calibrate_list = calibrate_list
        self.irradiation_film = irradiation_film
        self.setting_doses = doses_list
        self.sigma = sigma

    def run(self):
        """
        Start thread
        """
        self.red_channel_calc()
        self.calculate_calibrate_film()
        self.calc_dose_map()

    @staticmethod
    def fit_func(od, a, b, c):
        """
        Fitting function for calibration curve
        :param od:
        :param a:
        :param b:
        :param c:
        :return:
        """
        return (b / (od - a)) + c

    def red_channel_calc(self):
        """
        Calculate value in red channel of blank field
        :return: od_blank
        """
        blank_field_path = self.zero_dose
        im = tifimage.imread(blank_field_path)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        od_blank = np.mean(imarray)
        print("Blank field value: ", round(od_blank, 2))

        DosesAndPaths.red_channel_blank = od_blank
        return od_blank

    def calc_dose(self, path_to_film):
        """
        Image file processor
        """
        im = tifimage.imread(path_to_film)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        red_channel_current_tiff = np.mean(imarray)
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
            p_opt, p_cov = curve_fit(self.fit_func, np.array(DosesAndPaths.calculation_doses[1:]),
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
            user_img = self.irradiation_film
            zero_dose_for_irrad_film = self.calc_dose(self.zero_dose_for_irrad_film)
            im = tifimage.imread(user_img)
            imarray = np.array(im, dtype=np.uint16)
            imarray = (imarray[:, :, 0])

            print("\nShape of scanned film:", np.shape(imarray))
            progress = 0
            counter = 0
            print("\nPrepearing your file:\n")
            for i in np.nditer(imarray):
                x = np.log10(DosesAndPaths.red_channel_blank / i)
                x = x - zero_dose_for_irrad_film
                x = self.fit_func(x, *DosesAndPaths.p_opt)
                DosesAndPaths.z = np.append(DosesAndPaths.z, x)

                counter = counter + 1
                if counter % 10000 == 0:
                    print("Iteration ", counter, "/", np.size(imarray))
                    progress += 1
                    self.progressChanged.emit(round(progress))

            DosesAndPaths.z = DosesAndPaths.z.reshape(np.shape(imarray))
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
        index = self.gridLayout_3.count()
        if index != 5:
            for i in range(3):
                index -= 1
                my_widget = self.gridLayout_3.itemAt(index).widget()
                my_widget.setParent(None)
                self.adjustSize()

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

        DosesAndPaths.doses = doses
        DosesAndPaths.paths = paths
        DosesAndPaths.sigma = sigma
        DosesAndPaths.empty_scanner_field_file = self.lineEdit_2.text()
        DosesAndPaths.calculation_doses.clear()

        self.get_enabled_curve_drawing()

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
        if self.gridLayout_3.count() >= 5 and data_count > 1:
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

    def get_values(self):
        """
        Get the values of doses, calculation doses and p_opt in dialog window
        """
        self.value_win = ValuesWindow()
        if len(DosesAndPaths.calculation_doses) > 0:
            self.value_win.plainTextEdit.appendPlainText(('points: ' + str(DosesAndPaths.doses)))
            self.value_win.plainTextEdit.appendPlainText(('doses: ' + str(DosesAndPaths.calculation_doses)))
            self.value_win.plainTextEdit.appendPlainText(('p_opt: ' + str(DosesAndPaths.p_opt)))
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
                        DosesAndPaths.irrad_film_file, DosesAndPaths.sigma)
            calc.red_channel_calc()
            calc.calculate_calibrate_film()
            GraphicsPlotting.draw_curve(Dose.fit_func, DosesAndPaths.calculation_doses, DosesAndPaths.doses,
                                        DosesAndPaths.p_opt, self.figure_graph, self.canvas_graph, DosesAndPaths.sigma)
        except (ValueError, TypeError):
            print('Incorrect parameters')

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

    def draw_graphics(self, slice_x, slice_y):
        """
        Method for graphing the X and Y axes
        :param slice_x: Set of values along the X-axis
        :param slice_y: Set of values along the Y-axis
        """
        formatter = lambda x, pos: round(x * DosesAndPaths.basis_formatter, 3)  # the resolution

        # x axis
        self.figure_map_x.clf()
        ax_x = self.figure_map_x.add_subplot(111)
        ax_x.grid(True, linestyle="-.")
        ax_x.plot(slice_x)
        ax_x.xaxis.set_major_formatter(formatter)
        ax_x.yaxis.set_major_formatter(formatter)
        self.canvas_map_x.draw()
        self.pushButton.clicked.connect(lambda: self.get_values(slice_x, 'X axis'))

        # y axis
        self.figure_map_y.clf()
        ax_y = self.figure_map_y.add_subplot(111)
        ax_y.grid(True, linestyle="-.")
        ax_y.plot(slice_y)
        ax_y.xaxis.set_major_formatter(formatter)
        ax_y.yaxis.set_major_formatter(formatter)
        self.canvas_map_y.draw()
        self.pushButton_3.clicked.connect(lambda: self.get_values(slice_y, 'Y axis'))

    def get_values(self, values, ax_name):
        """
        Get the values of doses on the axis in dialog window
        :param values: values of doses
        :param ax_name: name of the axis
        """
        self.value_win = ValuesWindow()
        self.value_win.label.setText(ax_name)
        if len(values) > 0:
            self.value_win.plainTextEdit.appendPlainText(' '.join(map(str, values)))
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

    def __init__(self, *args, **kwargs):
        super(CalcUI, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.form = None
        self.graphic_dialog = None
        self.thread = None

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

        self.ax = self.figure_map.add_subplot(111)
        # Set cursor
        self.cursor = None

        self.ui.pushButton_7.clicked.connect(self.get_irrad_film_file)
        self.ui.pushButton.clicked.connect(self.get_empty_field_file)
        self.ui.pushButton_8.clicked.connect(self.get_dialog_window)
        self.ui.pushButton_4.clicked.connect(self.start_calc)
        self.ui.pushButton_9.clicked.connect(SaveLoadData.load_json)

    def get_irrad_film_file(self):
        """
        Find and paste the irradiate film file in tiff format
        """
        self.ui.lineEdit_3.setText(self.search_file('*.tif'))

        if len(self.ui.lineEdit_3.text()) != 0:
            DosesAndPaths.irrad_film_file = self.ui.lineEdit_3.text()
            self.ui.lineEdit_3.setDisabled(True)

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

    def insert_tiff_file(self):
        """
        Insert a picture of the film in the interface window
        """
        self.image_map.clf()
        img = plt.imread(DosesAndPaths.irrad_film_file)
        ax = self.image_map.add_subplot(111)
        ax.imshow(img)
        self.image_canvas.draw()

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

    def start_calc(self):
        """
        Running the calculation in the thread
        """
        if self.check_fields():
            self.get_dpi_value()

            DosesAndPaths.z = list()
            self.thread = Dose(DosesAndPaths.empty_scanner_field_file, DosesAndPaths.empty_field_file,
                               DosesAndPaths.paths, DosesAndPaths.doses,
                               DosesAndPaths.irrad_film_file,
                               DosesAndPaths.sigma)
            self.thread.start()
            self.thread.progressChanged.connect(self.progress_bar_update)
            self.insert_tiff_file()

    @staticmethod
    def check_fields():
        """
        Check fields for validity
        """
        if DosesAndPaths.empty_scanner_field_file is not None and DosesAndPaths.empty_field_file is not None \
                and DosesAndPaths.irrad_film_file is not None and len(DosesAndPaths.paths) > 0 \
                and len(DosesAndPaths.doses) > 0 and DosesAndPaths.basis_formatter > 0:
            return True


class SaveLoadData:
    """
    Сlass for save and load json
    """

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

        SaveLoadData.save_json(data)

    @staticmethod
    def save_json(data):
        """
        Save json file
        :param data: json object
        """
        filename, _ = QFileDialog.getSaveFileName(None, 'Save calibrate list and empty scanner field file',
                                                  'calibrate_and_empty.json',
                                                  'JSON files (*.json);;all files(*.*)',
                                                  options=QFileDialog.DontUseNativeDialog)
        if filename is not '':
            with open(filename, 'w') as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=4)

    @staticmethod
    def load_json():
        """
        Load and parse json file
        """
        data = application.search_file('*.json')

        if os.path.exists(data):
            with open(data) as f:
                data = json.load(f)
                for p in data['calibrate_list']:
                    DosesAndPaths.doses = [float(i) for i in p.keys()]
                    DosesAndPaths.paths = p.values()

                DosesAndPaths.sigma = data['sigma']
                DosesAndPaths.empty_scanner_field_file = data['empty_scanner_field_file']


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
