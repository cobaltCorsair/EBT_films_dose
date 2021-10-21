# Python 3.7
# -*- coding: utf-8 -*-
import os
import sys
import json
import matplotlib.pyplot as plt

plt.switch_backend('agg')
import numpy as np
import tifffile as tifimage
import matplotlib.widgets
from PyQt5.QtCore import pyqtSignal, QThread
from scipy.optimize import curve_fit
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QLineEdit, QDoubleSpinBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from Dose import Ui_MainWindow
from calibrate_list import Ui_Form
from Axes import Ui_Form as Axes_form
from Curve import Ui_Form as Curve_form


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
        im3 = ax.imshow(z, cmap="jet", vmin=0, vmax=2., interpolation="gaussian")
        application.figure_map.colorbar(im3, ax=ax, orientation="vertical")
        application.canvas_map.draw()

    @staticmethod
    def draw_curve(func, calculation_doses, setting_doses, p_opt, figure_graph, canvas_graph):
        """
        This method draws dose curve
        """
        figure_graph.clf()
        ax = figure_graph.add_subplot(111)
        ax.plot(calculation_doses, setting_doses, ".k", markersize=6, label="Measurements")
        ax.plot(calculation_doses, func(calculation_doses, *p_opt))
        ax.grid(True, linestyle="-.")
        ax.set_ylabel('Absorbed dose, Gy')
        ax.set_xlabel('Relative optical density')
        canvas_graph.draw()


class Dose(QThread):
    """
    Calculate dose
    """
    progressChanged = QtCore.pyqtSignal(int)

    def __init__(self, zero_dose, calibrate_list, doses_list, irradiation_film, sigma):
        super().__init__()
        self.zero_dose = zero_dose
        self.calibrate_list = calibrate_list
        self.irradiation_film = irradiation_film
        self.setting_doses = doses_list
        self.sigma = sigma

    def run(self):
        """
        Start thread
        """
        self.red_chanel_calc()
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

    def red_chanel_calc(self):
        """
        Calculate value in red channel of blank field
        :return:
        """
        blankFieldPath = self.zero_dose
        im = tifimage.imread(blankFieldPath)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        odBlank = np.mean(imarray)
        print("Blank field value: ", round(odBlank, 2))

        DosesAndPaths.od_blank = odBlank
        return odBlank

    def calc_dose(self, path_to_film):
        """
        Image file processor
        """
        im = tifimage.imread(path_to_film)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        od_current_dose = np.mean(imarray)
        od_current_dose = np.log10(DosesAndPaths.od_blank / od_current_dose)

        return od_current_dose

    def find_best_fit(self, path_to_film):
        od_current_dose = self.calc_dose(path_to_film) - self.zero_dose
        DosesAndPaths.calculation_doses.append(od_current_dose)

    def calculate_calibrate_film(self):
        """
        Calculating dose for each file
        """
        # сначала считаем нулевую дозу
        self.zero_dose = self.calc_dose(self.zero_dose)
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
        userImg = self.irradiation_film
        im = tifimage.imread(userImg)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])

        print("\nShape of scanned film:", np.shape(imarray))
        progress = 0
        counter = 0
        print("\nPrepearing your file:\n")

        for i in np.nditer(imarray):
            x = np.log10(DosesAndPaths.od_blank / i)
            x = x - self.zero_dose
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


class DosesAndPaths:
    """
    Data-class
    """
    empty_field_file = None
    irrad_film_file = None
    calculation_doses = list()
    od_blank = None
    p_opt = None
    doses = list()
    paths = list()
    sigma = 0
    z = list()


class Form(QtWidgets.QWidget, Ui_Form):
    """UI class for displaying dose/path list"""

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.widget_count = 0
        self.all_widgets = None
        self.curve_win = None

        self.pushButton_5.setDisabled(True)

        self.pushButton.clicked.connect(lambda: self.get_empty_field_file(self.lineEdit))
        self.pushButton_2.clicked.connect(self.dynamic_add_fields)
        self.pushButton_3.clicked.connect(self.dynamic_delete_fields)
        self.pushButton_4.clicked.connect(self.get_all_params_widgets)
        self.pushButton_5.clicked.connect(self.draw_curve)

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

    def dynamic_delete_fields(self):
        """
        Deleting fields to record paths/doses
        """
        index = self.gridLayout_3.count()
        if index != 5:
            for i in range(3):
                index -= 1
                myWidget = self.gridLayout_3.itemAt(index).widget()
                myWidget.setParent(None)
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
        self.curve_win.show()
        self.pushButton_5.setDisabled(True)

    def create_widgets_second_open(self):
        data_count = len(DosesAndPaths.doses)
        if self.gridLayout_3.count() >= 5 and data_count > 1:
            for i in range(data_count - 1):
                self.dynamic_add_fields()


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
            calc = Dose(DosesAndPaths.empty_field_file, DosesAndPaths.paths, DosesAndPaths.doses,
                        DosesAndPaths.irrad_film_file,
                        DosesAndPaths.sigma)
            calc.red_chanel_calc()
            calc.calculate_calibrate_film()
            GraphicsPlotting.draw_curve(Dose.fit_func, DosesAndPaths.calculation_doses, DosesAndPaths.doses,
                                        DosesAndPaths.p_opt, self.figure_graph, self.canvas_graph)
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
        self.figure_map_x.clf()
        ax_x = self.figure_map_x.add_subplot(111)
        ax_x.plot(slice_x)
        self.canvas_map_x.draw()

        self.figure_map_y.clf()
        ax_y = self.figure_map_y.add_subplot(111)
        ax_y.plot(slice_y)
        self.canvas_map_y.draw()

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

        self.scene = QtWidgets.QGraphicsScene()
        self.pixmap = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        self.ui.graphicsView.setScene(self.scene)

        self.figure_map = plt.figure()
        self.canvas_map = FigureCanvas(self.figure_map)
        self.toolbar_map = NavigationToolbar(self.canvas_map, self)
        self.ui.verticalLayout_2.addWidget(self.toolbar_map)
        self.ui.verticalLayout_2.addWidget(self.canvas_map)

        self.ax = self.figure_map.add_subplot(111)
        # Set cursor
        self.cursor = None

        self.ui.pushButton_5.clicked.connect(self.get_empty_field_file)
        self.ui.pushButton_7.clicked.connect(self.get_irrad_film_file)
        self.ui.pushButton_8.clicked.connect(self.get_dialog_window)
        self.ui.pushButton_4.clicked.connect(self.start_calc)
        self.ui.pushButton_2.clicked.connect(SaveLoadData.create_json)
        self.ui.pushButton_3.clicked.connect(SaveLoadData.load_json)

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
        self.ui.lineEdit_2.setText(self.search_file('*.tif'))

        if len(self.ui.lineEdit_2.text()) != 0:
            DosesAndPaths.empty_field_file = self.ui.lineEdit_2.text()
            self.ui.lineEdit_2.setDisabled(True)

    def insert_tiff_file(self):
        """
        Insert a picture of the film in the interface window
        """
        img = QtGui.QPixmap(DosesAndPaths.irrad_film_file)
        self.pixmap.setPixmap(img)

    def onclick(self, event, ax):
        """
        Place the cross cursor on the dose map
        :param event: onclick event
        ::param ax: existing dose map
        """
        if event.inaxes == ax and len(DosesAndPaths.z) > 1:
            try:
                self.cursor.onmove(event)
                x, y = int(event.xdata), int(event.ydata)
                slice_y = DosesAndPaths.z[:, x]
                slice_x = DosesAndPaths.z[y, :]

                self.graphic_dialog = AxesWindow()
                self.graphic_dialog.draw_graphics(slice_x, slice_y)
                self.graphic_dialog.show()
            except IndexError:
                print('Too many indices for array')

    def get_dialog_window(self):
        """
        Show dialog window with doses and paths
        """
        self.form = Form()
        self.form.create_widgets_second_open()
        self.insert_data_in_fields()
        self.form.show()

    def insert_data_in_fields(self):
        """
        Fill in the dialog window with doses and paths when opening
        """
        widgets = [self.form.gridLayout_3.itemAt(i).widget() for i in range(self.form.gridLayout_3.count())]
        lineedits = [i for i in widgets if isinstance(i, QLineEdit)]
        spinboxes = [i for i in widgets if isinstance(i, QDoubleSpinBox)]

        for path, dose, line, spin in zip(DosesAndPaths.paths, DosesAndPaths.doses, lineedits, spinboxes):
            if isinstance(line, QLineEdit):
                line.setText(path)
            if isinstance(spin, QDoubleSpinBox):
                spin.setValue((float(dose)))

        self.form.spinBox.setValue(DosesAndPaths.sigma)

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
        if DosesAndPaths.empty_field_file is not None and DosesAndPaths.irrad_film_file is not None \
                and len(DosesAndPaths.paths) > 0 and len(DosesAndPaths.doses) > 0:
            DosesAndPaths.z = list()
            self.thread = Dose(DosesAndPaths.empty_field_file, DosesAndPaths.paths, DosesAndPaths.doses,
                               DosesAndPaths.irrad_film_file,
                               DosesAndPaths.sigma)
            self.thread.start()
            self.thread.progressChanged.connect(self.progress_bar_update)
            self.insert_tiff_file()


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
        if DosesAndPaths.empty_field_file is not None:
            data['empty_field_file'] = DosesAndPaths.empty_field_file

        SaveLoadData.save_json(data)

    @staticmethod
    def save_json(data):
        """
        Save json file
        :param data: json object
        """
        filename, _ = QFileDialog.getSaveFileName(None, 'Save calibrate list and empty field file',
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
                DosesAndPaths.empty_field_file = data['empty_field_file']

                application.ui.lineEdit_2.setText(DosesAndPaths.empty_field_file)


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
# application.setMaximumSize(800, 600)
application.show()
sys.exit(app.exec())
