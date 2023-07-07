from PyQt5.QtWidgets import QMessageBox


class Warnings:
    """
    This class contains pop-up errors
    """

    @staticmethod
    def error_exist_files(file: list):
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

    @staticmethod
    def error_empty_image():
        QMessageBox.critical(None, "Data error", "<b>No data</b><br><br>"
                                                 "No unexposed film",
                             QMessageBox.Ok)

    @staticmethod
    def error_if_is_admin():
        QMessageBox.information(None, "Warning", "<b>Administrator rights are detected.</b><br><br>"
                                                 "The program is running with administrator privileges. "
                                                 "Enabled UAC with default settings does not allow access to mapped "
                                                 "(via net use) network drives from applications running in privileged "
                                                 "mode. Please run the program in normal mode, "
                                                 "or use files (or calibrations) that are not on a network drive.",
                                QMessageBox.Ok)

    @staticmethod
    def error_database_is_empty():
        QMessageBox.information(None, "Data error", "<b>Your database connections seems down...</b><br><br>"
                                                 "Seems that we cannot access your valid Mongo database"
                                                 "We are waiting generic network error time (aboud 30s) and if we "
                                                 "do not see your database is up, this button will be disabled for"
                                                 "the application lifetime."
                                                 "Ignore this if you intenionally want to use this program locally.",
                                QMessageBox.Ok)
        
    @staticmethod
    def error_database_is_empty():
        QMessageBox.information(None, "Data error", "<b>Your database connections seems down...</b><br><br>"
                                                 "Seems that we cannot access your valid Mongo database<br><br>"
                                                 "We are waiting or have been waited generic network error time "
                                                 " (aboud 30s) and if we do not see your database is up, this button <br>"
                                                 " will be disabled for the application lifetime. <br><br>"
                                                 "Ignore this if you intenionally want to use this program locally. <br>If you see this in eligible machine, please contact the developers<br><br>",
                                QMessageBox.Ok)        