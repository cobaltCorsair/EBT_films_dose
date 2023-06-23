from PyQt5 import QtWidgets
from DB_and_settings import Ui_Form as DB_form
from PyQt5.QtCore import pyqtSignal
from database import dbProxy as db
from database import db_connection
from SaveLoadData import SaveLoadData
from DosesAndPaths import DosesAndPaths
from logicParser import LogicODVariant, LogicCurveVariants, LogicCurveFitsVariant, LogicParser
from Warnings import Warnings
from ValuesWindow import ValuesWindow
from CurveWindow import CurveWindow

application = None
connect = False
try:
    collection = db_connection.Connect.start()
    connect = True
except Exception as e:
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print(message)

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
        facilities = db.getListOfFacilities(collection)
        return facilities

    def get_database_available_facilities_EVT4(self):
        """Load the available facilities from the database"""
        facilities = db.getListOfAvailableEBT4Facility(collection, self.comboBox.currentText())
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
        hours = db.getListOfAvailableHoursAfterIrradiation4FacilityAndLotNo(collection,
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
            return db.getData4CalibrationCurve(collection, self.comboBox.currentText(),
                                               self.comboBox_2.currentText(), int(self.comboBox_3.currentText()))
        elif method == 'zero_film':
            return db.getZeroFilmData4ExactLotNo(collection, self.comboBox.currentText(),
                                                 self.comboBox_2.currentText(), int(self.comboBox_3.currentText()))
        elif method == 'get_dict':
            return db.getDict4ExactCurveWithDoseLimit(collection, self.comboBox.currentText(),
                                                      self.comboBox_2.currentText(),
                                                      int(self.comboBox_3.currentText()), self.doubleSpinBox.value())

    def get_zero_film(self):
        """
        Get the first film from the calibration
        :return:
        """
        zero_from_db = db.getZeroFilmData4ExactLotNo(collection, self.comboBox.currentText(),
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

        #CalcUI.HAND_SWITCH_MODE = False
        application.HAND_SWITCH_MODE = False
        self.get_zero_film()
        # connect the buttons, because the calibration is correct
        application.ui.pushButton_8.setDisabled(False)
        application.ui.pushButton_4.setDisabled(False)

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
                if self.dose_curve_object.getPOpt() is not None:
                    self.value_win.plainTextEdit.appendPlainText(('\nPOLY_COEF_A_B_C: \n' + (
                        '\n'.join(map(str, [round(x, 4) for x in self.dose_curve_object.getPOpt()]))).replace('.',
                                                                                                              ',')))
            print(LogicParser.__dict__.keys())
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
