# Python 3.7
# -*- coding: utf-8 -*-
import importlib
import os
import sys
import ctypes
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QFileDialog, QInputDialog, QDialog, QVBoxLayout, 
                          QHBoxLayout, QPushButton, QPlainTextEdit, QMessageBox, QApplication)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import RectangleSelector
from Dose import Ui_MainWindow
from FileDialog import MyQFileDialog
from database import db_connection
from logicParser import LogicParser
from filters import Filters, Filter
from DosesAndPaths import DosesAndPaths
from GraphicsPlotting import GraphicsPlotting
import GraphicsPlotting as gp
import DoseClass as dc
from SaveLoadData import SaveLoadData
import SaveLoadData as sld
from DatabaseAndSettings import DatabaseAndSettings
import DatabaseAndSettings as das
from Warnings import Warnings
import Form as fm
from AxesWindow import AxesWindow
from stats import stats_ui
from stats import logicStats
from IsAdmin import IsAdmin

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
        Warnings.error_database_is_empty_readyfallback()

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
        self.ui.pushButton_6.clicked.connect(self.zone_operations)

        # @todo: implement 30 seconds timeout for connection as suggested in friendly messages
        # issued by .exe strange behaviour
        self.ui.pushButton_2.setDisabled(False)
        if CalcUI.connect:
            # self.ui.pushButton_2.setDisabled(False)
            pass
        else:
            Warnings.error_database_is_empty()
            self.ui.pushButton_2.setDisabled(True)
            pass

        IsAdmin.check_admin()

        # Изменяем текст кнопки на "Zone Operations"
        self.ui.pushButton_6.setText("Zone Operations")

    def get_irrad_film_file(self):
        """
        Find and paste the irradiate film file in tiff format
        """
        DosesAndPaths.irrad_film_array_original = None
        DosesAndPaths.irrad_film_array = None

        self.ui.lineEdit_3.setText(self.search_file('*.tif'))

        if len(self.ui.lineEdit_3.text()) != 0:
            DosesAndPaths.irrad_film_file = self.ui.lineEdit_3.text()
            DosesAndPaths.irrad_film_array_original = dc.Dose.get_imarray(DosesAndPaths.irrad_film_file)
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
                                    useblit=False, button=[1],
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

    def zone_operations(self):
        """
        Perform operations on selected zone using the RectangleSelector extents:
        1. Normalize image by coefficient
        2. Fit 2D Gaussian and analyze parameters
        """
        if self.start_pos is not None and self.end_pos is not None and self.start_pos[0] != self.end_pos[0]:
            try:
                if len(DosesAndPaths.z) == 0:
                    raise TypeError

                xmin, xmax, ymin, ymax = self.RS.extents
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)
                xnmin = xmin - int(self.pic_ax.get_xlim()[0])
                ynmin = ymin - int(self.pic_ax.get_ylim()[1])
                
                # Добавляем диалог для выбора режима работы: нормализация или 2D Gauss
                mode_options = ["Normalize by coefficient", "2D Gaussian fit"]
                selected_mode, ok_pressed = QInputDialog.getItem(self, 
                                                               "Select mode", 
                                                               "Choose operation:", 
                                                               mode_options, 
                                                               0, 
                                                               False)
                if not ok_pressed:
                    return
                
                # Если выбрана нормализация - используем старый код
                if selected_mode == "Normalize by coefficient":
                    curCf = LogicParser.getCurrentAverageByZone(DosesAndPaths.z, ynmin, xnmin, ymax - ymin, xmax - xmin)
                    curMax = LogicParser.getCurrentMaximumByZone(DosesAndPaths.z, ynmin, xnmin, ymax - ymin, xmax - xmin)
                    curMin = LogicParser.getCurrentMinimumByZone(DosesAndPaths.z, ynmin, xnmin, ymax - ymin, xmax - xmin)
                    cf, ok_pressed = QInputDialog.getDouble(self,
                                                            "Get coefficient",
                                                            "Max: %1.4f\nMin: %1.4f\nValue of cf:" % (curMax, curMin, ),
                                                            curCf,
                                                            float('-inf'),
                                                            float('inf'),
                                                            3)
                    if not ok_pressed:
                        return

                    # Normalize the image using the selected zone (order for numpy array y, x, h, w)
                    normalized_image = LogicParser.getNormalizedByZone(DosesAndPaths.z, ynmin, xnmin,
                                                                       ymax - ymin, xmax - xmin, cf=cf)
                    DosesAndPaths.z = normalized_image
                    GraphicsPlotting.draw_dose_map(normalized_image)
                # Если выбран 2D Gaussian fit - используем новый код
                elif selected_mode == "2D Gaussian fit":
                    # Проверяем, нужно ли выполнить пересчет дозы
                    recalc_dose = False
                    if len(DosesAndPaths.z) == 0 or not any(DosesAndPaths.z.flatten() != 0):
                        recalc_dose = True
                    else:
                        recalc_question = QMessageBox.question(
                            self, 
                            "Recalculate dose?", 
                            "Do you want to recalculate the dose before Gaussian fitting?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.Yes
                        )
                        if recalc_question == QMessageBox.Yes:
                            recalc_dose = True
                        else:
                            # Если пользователь ответил "No", прекращаем выполнение функции
                            return
                    
                    # Если нужно пересчитать дозу, вызываем start_calc
                    if recalc_dose:
                        self.start_calc()
                        # Даем немного времени для обновления интерфейса и завершения расчета
                        QtWidgets.QApplication.processEvents()
                    
                    # Получаем выбранную область из дозовой карты, используя смещенные координаты
                    # как это сделано в режиме нормализации
                    selected_area = DosesAndPaths.z[ynmin:ynmin+(ymax-ymin), xnmin:xnmin+(xmax-xmin)]
                    
                    # Создаем координатную сетку для 2D гаусса
                    x = np.arange(0, selected_area.shape[1])
                    y = np.arange(0, selected_area.shape[0])
                    xy = np.meshgrid(x, y)
                    
                    # Вычисляем параметры 2D гаусса
                    try:
                        params, errors = logicStats.prepareGauss2DFull(xy, selected_area)
                        
                        # Создаем форматтер для преобразования пикселей в мм
                        formatter = lambda x, _: round(x * DosesAndPaths.basis_formatter, 2)
                        
                        # Создаем строку для отображения результатов
                        result_text = f"2D Gaussian parameters:\n\n"
                        result_text += f"Amplitude: {params[0]:.4f} ± {errors[0]:.4f}\n"
                        
                        # Пересчитанные в мм координаты центра
                        x0_mm = formatter(params[1], None)
                        y0_mm = formatter(params[2], None)
                        x0_err_mm = formatter(errors[1], None)
                        y0_err_mm = formatter(errors[2], None)
                        
                        result_text += f"X₀: {params[1]:.4f} px ({x0_mm:.4f} mm) ± {errors[1]:.4f} px ({x0_err_mm:.4f} mm)\n"
                        result_text += f"Y₀: {params[2]:.4f} px ({y0_mm:.4f} mm) ± {errors[2]:.4f} px ({y0_err_mm:.4f} mm)\n"
                        
                        # Пересчитанные в мм сигмы
                        sigma_x_mm = formatter(params[3], None)
                        sigma_y_mm = formatter(params[4], None)
                        sigma_x_err_mm = formatter(errors[3], None)
                        sigma_y_err_mm = formatter(errors[4], None)
                        
                        result_text += f"σₓ: {params[3]:.4f} px ({sigma_x_mm:.4f} mm) ± {errors[3]:.4f} px ({sigma_x_err_mm:.4f} mm)\n"
                        result_text += f"σᵧ: {params[4]:.4f} px ({sigma_y_mm:.4f} mm) ± {errors[4]:.4f} px ({sigma_y_err_mm:.4f} mm)\n"
                        result_text += f"Offset: {params[5]:.4f} ± {errors[5]:.4f}\n\n"
                        
                        # Пересчитанные в мм FWHM
                        fwhm_x = 2.355 * params[3]
                        fwhm_y = 2.355 * params[4]
                        fwhm_x_mm = formatter(fwhm_x, None)
                        fwhm_y_mm = formatter(fwhm_y, None)
                        
                        result_text += f"FWHM_x: {fwhm_x:.4f} px ({fwhm_x_mm:.4f} mm)\n"
                        result_text += f"FWHM_y: {fwhm_y:.4f} px ({fwhm_y_mm:.4f} mm)\n"
                        
                        # Показываем результаты в текстовом диалоге
                        result_dialog = QDialog(self)
                        result_dialog.setWindowTitle("2D Gaussian Fit Results")
                        layout = QVBoxLayout(result_dialog)
                        
                        text_edit = QPlainTextEdit()
                        text_edit.setReadOnly(True)
                        text_edit.setPlainText(result_text)
                        font = QFont("Monospace")
                        font.setStyleHint(QFont.TypeWriter)
                        text_edit.setFont(font)
                        
                        copy_button = QPushButton("Copy to Clipboard")
                        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(result_text))
                        
                        close_button = QPushButton("Close")
                        close_button.clicked.connect(result_dialog.close)
                        
                        button_layout = QHBoxLayout()
                        button_layout.addWidget(copy_button)
                        button_layout.addWidget(close_button)
                        
                        layout.addWidget(text_edit)
                        layout.addLayout(button_layout)
                        
                        result_dialog.setLayout(layout)
                        result_dialog.resize(400, 400)
                        result_dialog.exec_()
                        
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to fit 2D Gaussian: {str(e)}")
            except TypeError:
                Warnings.inform_about_normalize()
        else:
            Warnings.inform_about_area()

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
        return

    def get_dialog_window(self):
        """
        Show dialog window with doses and paths
        """
        self.form = fm.Form()
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

        self.select_filter()

    def calc_from_manual(self):
        """
        Calculate from manual mode
        """
        self.get_dpi_value()
        DosesAndPaths.z = list()
        self.thread = dc.Dose(DosesAndPaths.empty_scanner_field_file, DosesAndPaths.empty_field_file,
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
        try:
            self.bd_win = DatabaseAndSettings()
            self.bd_win.show()
        except:
            Warnings.error_database_is_empty()

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
    dc.application = application
    application.setWindowTitle("Dose calculator")
    # set minimum size
    application.setMinimumSize(1200, 800)
    application.show()
    sys.exit(app.exec())
