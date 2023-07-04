from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu
from PyQt5.QtCore import Qt
from DosesAndPaths import DosesAndPaths
from stats import logicStats
import numpy as np


class PanelWindow(QWidget):
    def __init__(self, main_window, axes_window, position='right'):
        """
        Initializer for the PanelWindow class. This function sets the default values for the panel window and creates
        widgets that are used in the window.
        :param main_window: Parent window to the panel window
        :param axes_window: Reference to the window which will be updated when checkboxes are clicked
        :param position: The position of the window relative to the main window. Default is 'right'.
        """
        super(PanelWindow, self).__init__()
        self.setFixedWidth(200)  # Set the width of the panel
        self.setFixedHeight(350)
        self.setStyleSheet("background-color: #f0f0f0;")  # Just to distinguish the panel

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Name", "Value"])

        self.stats_item = QTreeWidgetItem(self.tree)
        self.stats_item.setText(0, "Stats")

        self.min_item = QTreeWidgetItem(self.stats_item)
        self.min_item.setText(0, "Minimum")
        self.min_item.setText(1, "0")

        self.max_item = QTreeWidgetItem(self.stats_item)
        self.max_item.setText(0, "Maximum")
        self.max_item.setText(1, "0")

        self.median_item = QTreeWidgetItem(self.stats_item)
        self.median_item.setText(0, "Median")
        self.median_item.setText(1, "0")

        self.gauss_item = QTreeWidgetItem(self.tree)
        self.gauss_item.setText(0, "Gauss")
        self.gauss_item.setCheckState(0, Qt.Unchecked)

        self.constant_item = QTreeWidgetItem(self.gauss_item)
        self.constant_item.setText(0, "Constant")
        self.constant_item.setText(1, "0")
        self.constant_item.setHidden(True)

        self.sigma_item = QTreeWidgetItem(self.gauss_item)
        self.sigma_item.setText(0, "Sigma")
        self.sigma_item.setText(1, "0")
        self.sigma_item.setHidden(True)

        self.mu_item = QTreeWidgetItem(self.gauss_item)
        self.mu_item.setText(0, "Mu")
        self.mu_item.setText(1, "0")
        self.mu_item.setHidden(True)

        self.poly_item = QTreeWidgetItem(self.tree)
        self.poly_item.setText(0, "Polynomial N")
        self.poly_item.setCheckState(0, Qt.Unchecked)

        self.cf_items = []
        for i in range(5):
            cf_item = QTreeWidgetItem(self.poly_item)
            cf_item.setText(0, f"cf{i}")
            cf_item.setText(1, "0")
            cf_item.setHidden(True)
            self.cf_items.append(cf_item)

        # Add an attribute to keep track of which checkbox is associated with this instance
        self.checkbox_position = position
        self.gauss_checked = False
        self.poly_checked = True

        self.tree.itemChanged.connect(self.handle_item_changed)
        self.tree.itemDoubleClicked.connect(self.handle_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tree)

        self.position = position
        self.main_window = main_window
        self.axes_window = axes_window

        self.dataChangedLeft = axes_window.dataChangedLeft
        self.dataChangedRight = axes_window.dataChangedRight

        # Initialize lines to None
        self.line_x = None
        self.line_y = None

        # Add these two lines
        self.dataChangedLeftConnected = False
        self.dataChangedRightConnected = False

    def handle_item_changed(self, item, column):
        """
        Event handler function for changes in items in the QTreeWidget.
        :param item: The item that was changed
        :param column: The column of the item that was changed
        """
        if column == 0 and item == self.gauss_item:
            hidden = item.checkState(0) == Qt.Unchecked
            self.gauss_checked = not hidden
            if hidden:
                self.handle_unchecked()
                self.constant_item.setHidden(True)
                self.sigma_item.setHidden(True)
                self.mu_item.setHidden(True)
            elif not hidden:
                self.handle_checked()
                self.constant_item.setHidden(False)
                self.sigma_item.setHidden(False)
                self.mu_item.setHidden(False)
            self.handle_data_changed(self.position)

    def handle_unchecked(self):
        """
        Event handler function for when the checkbox in the panel window is unchecked.
        """
        if self.position == 'left' and self.dataChangedLeftConnected:
            self.dataChangedLeft.disconnect(self.handle_data_changed)
            self.dataChangedLeftConnected = False
            self.remove_line(self.axes_window.ax_x, 'x')

        elif self.position == 'right' and self.dataChangedRightConnected:
            self.dataChangedRight.disconnect(self.handle_data_changed)
            self.dataChangedRightConnected = False
            self.remove_line(self.axes_window.ax_y, 'y')

    def handle_checked(self):
        """
        Event handler function for when the checkbox in the panel window is checked.
        """
        if self.position == 'left':
            self.dataChangedLeft.connect(self.handle_data_changed)
            self.dataChangedLeftConnected = True
        elif self.position == 'right':
            self.dataChangedRight.connect(self.handle_data_changed)
            self.dataChangedRightConnected = True

    def remove_line(self, ax, axis):
        """
        Function for removing a line from a given axis.
        :param ax: The axis from which to remove the line
        :param axis: A string indicating the type of axis (x or y)
        """
        line = self.line_x if axis == 'x' else self.line_y
        if line is not None:
            if line in ax.lines:
                line.remove()
                if axis == 'x':
                    self.line_x = None  # Reset to None
                else:
                    self.line_y = None  # Reset to None
            ax.figure.canvas.draw()  # Update the canvas

    def handle_item_double_clicked(self, item, column):
        if column == 1:  # Only allow copying from the Value column
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text(column))

    def open_menu(self, position):
        """
        Function to create and open a context menu at the given position.
        :param position: The position to open the menu at.
        """
        menu = QMenu()
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy_item_text)
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def copy_item_text(self):
        """
        Function to copy the current item's text to clipboard.
        """
        item = self.tree.currentItem()
        if item is not None and item.columnCount() > 1:  # Make sure item and Value column exist
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text(1))  # Copy text from Value column

    def handle_data_changed(self, position):
        """
        Event handler function for when the data is changed.
        :param position: The position of the window that triggered the event
        """
        if not self.gauss_checked or position != self.checkbox_position:
            return
        
        from logicStats import universalFunctions as u
        from logicStats import universalStats as s
          
        if position == 'left':
            mvdx = self.axes_window.formatted_mvdx_x
            final_slice_values = DosesAndPaths.final_slice_values_x
            ax = self.axes_window.ax_x
        elif position == 'right':
            mvdx = self.axes_window.formatted_mvdx_y
            final_slice_values = DosesAndPaths.final_slice_values_y
            ax = self.axes_window.ax_y

        if mvdx is not None:
            if self.gauss_checked:
                v = s(np.array([mvdx, final_slice_values]), u.gauss, basisFormatter=DosesAndPaths.basis_formatter)
                v.run()
                cfs, errs = v.getMeDataForPrinting()
                self.constant_item.setText(1, f"{cfs[0]:.3f} ± {errs[0]:.3f}")
                self.mu_item.setText(1, f"{cfs[1]:.3f} ± {errs[1]:.3f}")
                self.sigma_item.setText(1, f"{cfs[2]:.3f} ± {errs[2]:.3f}")
                self.plot_additional_data(ax, v, kind=v.gauss)

            if self.poly_checked:
                pass

    def mm_to_pixels(self, value):
        """
        Utility function for converting millimeters to pixels.
        :param value: The value in millimeters to convert to pixels
        :return: The converted value in pixels
        """
        return round(value / DosesAndPaths.basis_formatter, 0)

    def plot_additional_data(self, ax, v, kind=v.basic, color="r"):
        """
        Function for plotting additional data on a given axis.
        :param ax: The axis on which to plot the data
        :param v: object of our current fitting state  
        :type v: logicStats.universalStats
        :param kind: kind of fit in enum format
        :type kind: logicStats.universalFunctions 
        """
        # Check if line exists and update data
        if kind == v.gauss:
            o = v.getMeDataForMatplotlibPlot()
            if self.line_x is not None and ax == self.axes_window.ax_x:
                self.line_x.set_xdata(o[0])
                self.line_x.set_ydata(o[1])
            elif self.line_y is not None and ax == self.axes_window.ax_y:
                self.line_y.set_xdata(o[0])
                self.line_y.set_ydata(o[1])
            else:  # Line does not exist, create it
                er = getMeDataForPrinting()
                if ax == self.axes_window.ax_x:
                    self.line_x, = ax.plot(o[0], o[1], color)
                elif ax == self.axes_window.ax_y:
                    self.line_y, = ax.plot(o[0], o[1], color)
        if kind == v.residual:   
            o = v.getMeDataForMatplotlibPlot()
            if self.line_x is not None and ax == self.axes_window.ax_x:
                self.line_x.set_xdata(o[0])
                self.line_x.set_ydata(o[1])
            elif self.line_y is not None and ax == self.axes_window.ax_y:
                self.line_y.set_xdata(o[0])
                self.line_y.set_ydata(o[1])
            else:  # Line does not exist, create it
                if ax == self.axes_window.ax_x:
                    self.line_x, = ax.plot(*o)
                elif ax == self.axes_window.ax_y:
                    self.line_y, = ax.plot(*o)


        ax.figure.canvas.draw()


class MainWindow(QWidget):
    def __init__(self, button, axes_window, position='right'):
        """
        Initializer for the MainWindow class. This function sets the default values for the main window and creates
        widgets that are used in the window.
        :param button: Button widget that will be used to show the panel
        :param axes_window: Reference to the window which will be updated when checkboxes are clicked
        :param position: The position of the window relative to the main window. Default is 'right'.
        """
        super(MainWindow, self).__init__()
        self.panel = PanelWindow(self, axes_window=axes_window, position=position)
        self.panel.setWindowTitle("Stats " + ('Y' if position == 'right' else 'X'))
        self.panel.hide()

        self.button = button
        self.position = position

    def show_panel(self):
        """
        Function for showing the panel window. The position of the panel window is calculated based on the position of
        the button in the main window and the position property of the panel window.
        """
        # Move the panel to the right of the button
        if self.position == 'right':
            self.panel.move(
                self.button.mapToGlobal(self.button.rect().topRight()))
        else:
            # Move the panel to the left of the button
            self.panel.move(self.button.mapToGlobal(
                self.button.rect().topLeft()) - self.panel.rect().topRight())
        self.panel.show()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
