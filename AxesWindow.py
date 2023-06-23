from PyQt5 import QtWidgets
from Axes import Ui_Form as Axes_form
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from DosesAndPaths import DosesAndPaths
from SaveLoadData import SaveLoadData
from MoveGraphLine import MoveGraphLine
import numpy as np
from ValuesWindow import ValuesWindow

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

        self.formatted_mvdx = None

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
            graf, = ax.plot(slice_clipped)
            return graf, slice_clipped
        else:
            graf, = ax.plot(slice)
            return graf, slice

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
        graf_x, slice_values_x = AxesWindow.dose_limits_for_graph(slice_x, ax_x)
        ax_x.xaxis.set_major_formatter(formatter)
        ax_x.set_xlabel('mm')
        ax_x.set_ylabel('Absorbed dose, Gy')
        self.canvas_map_x.draw()
        self.pushButton.clicked.connect(lambda: self.get_values(slice_values_x, 'X axis'))
        self.pushButton_2.clicked.connect(lambda: SaveLoadData.save_as_excel_file_axis(slice_values_x,
                                                                                       'X axis', self.formatted_mvdx))

        # Add a function to move the X diagram along the X axis
        self.moveline_x_x = MoveGraphLine(graf_x, ax_x, move_speed=0.1)
        self.moveline_x_x.dataChanged.connect(self.handle_data_changed)

        # y axis
        self.figure_map_y.clf()
        ax_y = self.figure_map_y.add_subplot(111)
        ax_y.grid(True, linestyle="-.")
        graf_y, slice_values_y = AxesWindow.dose_limits_for_graph(slice_y, ax_y)
        ax_y.xaxis.set_major_formatter(formatter)
        ax_y.set_xlabel('mm')
        ax_y.set_ylabel('Absorbed dose, Gy')
        self.canvas_map_y.draw()
        self.pushButton_3.clicked.connect(lambda: self.get_values(slice_values_y, 'Y axis'))
        self.pushButton_4.clicked.connect(lambda: SaveLoadData.save_as_excel_file_axis(slice_values_y,
                                                                                       'Y axis', self.formatted_mvdx))

        # Add a function to move the Y diagram along the X axis
        self.moveline_x_y = MoveGraphLine(graf_y, ax_y, move_speed=0.1)
        self.moveline_x_y.dataChanged.connect(self.handle_data_changed)

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

    def handle_data_changed(self, mvdx, mvdy):
        # Multiply the raw x-axis data (mvdx) by the basis
        # formatter to convert the values to the desired scale
        formatted_mvdx = mvdx * DosesAndPaths.basis_formatter

        # Round the formatted x-axis data to 0 decimal
        # places and store it as an attribute of the class
        self.formatted_mvdx = formatted_mvdx.round(2)