from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
import numpy as np

class MoveGraphLine(QtWidgets.QWidget):
    """
    Adds functionality to move graphs along the X-axis.
    """
    dataChanged = pyqtSignal(np.ndarray, np.ndarray)

    def __init__(self, graf, ax, move_speed=0.5):
        QtWidgets.QWidget.__init__(self)
        self.graf = graf  # The graph to be moved
        self.ax = ax  # The axes object of the graph
        self.figcanvas = self.ax.figure.canvas  # The canvas of the figure
        self.start_point = None  # The starting point of the mouse drag
        self.move_speed = move_speed  # The speed of the graph movement
        self.moving = False  # Flag indicating whether the graph is moving or not

        # Connect the mouse events to their respective handlers
        self.figcanvas.mpl_connect('button_press_event', self.mouse_press)
        self.figcanvas.mpl_connect('button_release_event', self.mouse_release)
        self.figcanvas.mpl_connect('motion_notify_event', self.mouse_move)

    def mouse_release(self, event):
        # Check if a navigation tool is active, if so, do nothing
        if self.ax.get_navigate_mode() is not None:
            return
        self.moving = False

    def mouse_press(self, event):
        # Check if a navigation tool is active, if so, do nothing
        if self.ax.get_navigate_mode() is not None:
            return
        if event.inaxes != self.ax:
            return
        self.start_point = (event.xdata, event.ydata)
        self.moving = True

    def mouse_move(self, event):
        # Check if a navigation tool is active, if so, do nothing
        if self.ax.get_navigate_mode() is not None:
            return
        if event.inaxes != self.ax:
            return
        if not self.moving:
            return

        # Calculate the shift in the x-axis based on the mouse movement
        shift_x = (self.start_point[0] - event.xdata) * self.move_speed
        mvdx, mvdy = self.graf.get_data()  # Get the current graph data
        mvdx -= shift_x  # Update the x-axis data by applying the shift

        # Update the graph with the new data and redraw the canvas
        self.graf.set_data(mvdx, mvdy)
        self.figcanvas.draw()

        # Emit the dataChanged signal with the updated data
        self.dataChanged.emit(mvdx, mvdy)

