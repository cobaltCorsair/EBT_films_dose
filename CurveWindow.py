from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ui.Curve import Ui_Form as Curve_form
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from DosesAndPaths import DosesAndPaths
from DoseClass import Dose
from Warnings import Warnings
from GraphicsPlotting import GraphicsPlotting


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