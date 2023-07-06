# Python 3.7
# -*- coding: utf-8 -*-
import importlib
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import RectangleSelector
from Dose import Ui_MainWindow
from FileDialog import MyQFileDialog
from IsAdmin import IsAdmin
from database import db_connection
from logicParser import LogicParser
from filters import Filters, Filter
from DosesAndPaths import DosesAndPaths
from GraphicsPlotting import GraphicsPlotting
import GraphicsPlotting as gp
from DoseClass import Dose
from SaveLoadData import SaveLoadData
import SaveLoadData as sld
from DatabaseAndSettings import DatabaseAndSettings
import DatabaseAndSettings as das
from Warnings import Warnings
from Form import Form
import Form as fm
from AxesWindow import AxesWindow

plt.switch_backend('agg')


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

        IsAdmin.check_admin()

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
        file_name = MyQFileDialog.getOpenFileName(
            parent=self,
            caption='Open file',
            filter=file_type,
            options=QFileDialog.DontUseNativeDialog
        )[0]
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
        if self.ui.checkBox.isChecked() and application.HAND_SWITCH_MODE:
            try:
                DosesAndPaths.empty_field_file = DosesAndPaths.paths[0]
            except (TypeError, IndexError):
                Warnings.error_confirm_calibration()

        elif self.ui.checkBox.isChecked() and not application.HAND_SWITCH_MODE:
            DosesAndPaths.empty_field_file = DosesAndPaths.zero_from_db
        elif not self.ui.checkBox.isChecked() and len(self.ui.lineEdit.text()) is not 0:
            DosesAndPaths.empty_field_file = self.ui.lineEdit.text()
        else:
            Warnings.error_empty_film()

    def start_calc(self):
        """
        Running the calculation in the thread
        """
        self.get_vmin_vmax_values()

        if self.ui.checkBox_3.isChecked():
            try:
                self.calc_ODOnly()
                return
            except AttributeError:
                Warnings.error_empty_image()
                return

        self.first_film_from_calibration()

        if self.check_fields_manual_mode() and application.HAND_SWITCH_MODE:
            # manual mode
            self.calc_from_manual()

        if self.check_fields_bd_mode() and not application.HAND_SWITCH_MODE:
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
        im_arr_first = self.add_filter(CalcUI.choose_orig_or_crop())
        im_arr_flatt = im_arr_first.flatten()
        parsed_empty_file = empty_file
        z_object = DosesAndPaths.curve_object.preparePixValue(im_arr_flatt, parsed_empty_file)
        DosesAndPaths.z = (DosesAndPaths.curve_object.evaluateOD(z_object)).reshape(im_arr_first.shape)
        GraphicsPlotting.draw_dose_map(DosesAndPaths.z)
        self.progress_bar_update(100)

    def calc_ODOnly(self):
        """
        Setting z-data to np.log10(65535./PV) for all data
        @return: None
        """
        DosesAndPaths.z = []
        self.get_dpi_value()
        im_arr_first = self.add_filter(CalcUI.choose_orig_or_crop())
        im_arr_flatt = im_arr_first.flatten()
        # z_object = DosesAndPaths.curve_object.preparePixValue(im_arr_flatt)
        z_object = np.log10(65535. / im_arr_flatt)
        DosesAndPaths.z = z_object.reshape(im_arr_first.shape)
        GraphicsPlotting.draw_dose_map(DosesAndPaths.z)
        self.progress_bar_update(100)

    def add_filter(self, image_arr):
        """
        Adding a filter to an image
        :param image_arr: imarray
        :return:
        """
        with_filter = Filter(image_arr)
        with_filter.setFilter(Filters.__dict__[self.ui.comboBox.currentText()])
        with_filter.parse()
        return with_filter.get()

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


if __name__ == "__main__":
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash

        pyi_splash.close()

    basedir = os.path.dirname(__file__)
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    app.processEvents()
    app_icon = QIcon(os.path.join(basedir, "icon", "icon64x64.ico"))
    app.setWindowIcon(app_icon)
    application = CalcUI()
    # win title
    gp.application = application
    sld.application = application
    das.application = application
    fm.application = application
    application.setWindowTitle("Dose calculator")
    # set minimum size
    application.setMinimumSize(1200, 800)
    application.show()
    sys.exit(app.exec())
