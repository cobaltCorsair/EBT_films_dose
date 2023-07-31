from DosesAndPaths import DosesAndPaths
from PyQt5.QtWidgets import QFileDialog
import json
import os
from Warnings import Warnings
import pandas
from FileDialog import MyQFileDialog

application = None


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
        filename, _ = MyQFileDialog.getSaveFileName(file_name + '.json', None, 'Save calibrate setting or list',
                                                    filter='JSON files (*.json);;all files(*.*)',
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

                # connect the buttons, because the calibration is correct
                application.ui.pushButton_8.setDisabled(False)
                application.ui.pushButton_4.setDisabled(False)

            if not os.path.exists(data['empty_scanner_field_file']):
                not_exist_files.append(data['empty_scanner_field_file'])

        for i in DosesAndPaths.paths:
            if not os.path.exists(i):
                not_exist_files.append(i)

        if not_exist_files:
            Warnings().error_exist_files(not_exist_files)
            # disconnect the buttons, because the calibration is incorrect
            application.ui.pushButton_8.setDisabled(True)
            application.ui.pushButton_4.setDisabled(True)

    @staticmethod
    def save_db_win_setting(facility, lot, hours, dose_limit, od, fit_func, fitting):
        """
        Saving values in the database settings window
        :param facility: facility name
        :param lot: lot number
        :param hours: hours after irradiation
        :param dose_limit: dose limit
        :param od: optical density
        :param fit_func: type of fitting function
        :param fitting: function
        :return:
        """
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
            dataframe_array = pandas.DataFrame(DosesAndPaths.z)

            filename, _ = MyQFileDialog.getSaveFileName('dose_data', None, 'Save calibrate setting or list',
                                                        filter='Excel Files (*.xlsx);;all files(*.*)',
                                                        options=QFileDialog.DontUseNativeDialog)
            if filename is not '':
                try:
                    dataframe_array.to_excel(excel_writer=filename + '.xlsx')
                except OSError:
                    Warnings.error_special_symbols()
        else:
            Warnings.error_empty_dose()

    @staticmethod
    def save_as_excel_file_axis(ax, ax_name, formatted_mvdx):
        """
        Save axis as xlsx file
        :param ax: doses on the axis
        :param ax_name: axis name
        :param formatted_mvdx: formatted x-axis data
        """
        if len(ax) > 0:
            if formatted_mvdx is not None:
                ax_data = {'X': formatted_mvdx, 'Y': ax}
                ax_dataframe = pandas.DataFrame(ax_data)
            else:
                ax_dataframe = pandas.DataFrame(ax)

            filename, _ = MyQFileDialog.getSaveFileName(ax_name, None, 'Save calibrate setting or list',
                                                        filter='Excel Files (*.xlsx);;all files(*.*)',
                                                        options=QFileDialog.DontUseNativeDialog)
            if filename is not '':
                try:
                    ax_dataframe.to_excel(excel_writer=filename + '.xlsx')
                except OSError:
                    Warnings.error_special_symbols()
        else:
            Warnings.error_empty_dose()
