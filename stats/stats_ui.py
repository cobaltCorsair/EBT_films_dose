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

        self.mean_item = QTreeWidgetItem(self.stats_item)
        self.mean_item.setText(0, "Mean")
        self.mean_item.setText(1, "0")

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

        self.fwhm_item = QTreeWidgetItem(self.gauss_item)
        self.fwhm_item.setText(0, "FWHM")
        self.fwhm_item.setText(1, "0")
        self.fwhm_item.setHidden(True)

        self.poly_item = QTreeWidgetItem(self.tree)
        self.poly_item.setText(0, "Polynomial N")
        self.poly_item.setCheckState(0, Qt.Unchecked)

        self.gaussWithZero_item = QTreeWidgetItem(self.tree)
        self.gaussWithZero_item.setText(0, "Gauss with y0")
        self.gaussWithZero_item.setCheckState(0, Qt.Unchecked)

        self.constantWithZero_item = QTreeWidgetItem(self.gaussWithZero_item)
        self.constantWithZero_item.setText(0, "Constant")
        self.constantWithZero_item.setText(1, "0")
        self.constantWithZero_item.setHidden(True)
        self.sigmaWithZero_item = QTreeWidgetItem(self.gaussWithZero_item)
        self.sigmaWithZero_item.setText(0, "Sigma")
        self.sigmaWithZero_item.setText(1, "0")
        self.sigmaWithZero_item.setHidden(True)
        self.muWithZero_item = QTreeWidgetItem(self.gaussWithZero_item)
        self.muWithZero_item.setText(0, "Mu")
        self.muWithZero_item.setText(1, "0")
        self.muWithZero_item.setHidden(True)
        self.ynodWithZero_item = QTreeWidgetItem(self.gaussWithZero_item)
        self.ynodWithZero_item.setText(0, "y0")
        self.ynodWithZero_item.setText(1, "0")
        self.ynodWithZero_item.setHidden(True)
        self.fwhmWithZero_item = QTreeWidgetItem(self.gaussWithZero_item)
        self.fwhmWithZero_item.setText(0, "FWHM")
        self.fwhmWithZero_item.setText(1, "0")
        self.fwhmWithZero_item.setHidden(True)

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
        self.poly_checked = False
        self.gaussWithZero_checked = False

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
                self.fwhm_item.setHidden(True)
            elif not hidden:
                self.handle_checked()
                self.constant_item.setHidden(False)
                self.sigma_item.setHidden(False)
                self.mu_item.setHidden(False)
                self.fwhm_item.setHidden(False)
            self.handle_data_changed(self.position)
        if column == 0 and item == self.poly_item:
            hidden = item.checkState(0) == Qt.Unchecked
            self.poly_checked = not hidden
            if hidden:
                self.handle_unchecked()
                self.cf_items[0].setHidden(True)
                self.cf_items[1].setHidden(True)
                self.cf_items[2].setHidden(True)
                self.cf_items[3].setHidden(True)
            elif not hidden:
                self.handle_checked()
                self.cf_items[0].setHidden(False)
                self.cf_items[1].setHidden(False)
                self.cf_items[2].setHidden(False)
                self.cf_items[3].setHidden(False)
            self.handle_data_changed(self.position)
        if column == 0 and item == self.gaussWithZero_item:
            hidden = item.checkState(0) == Qt.Unchecked
            self.gaussWithZero_checked = not hidden
            if hidden:
                self.handle_unchecked()
                self.constantWithZero_item.setHidden(True)
                self.sigmaWithZero_item.setHidden(True)
                self.muWithZero_item.setHidden(True)
                self.fwhmWithZero_item.setHidden(True)
                self.ynodWithZero_item.setHidden(True)
            elif not hidden:
                self.handle_checked()
                self.constantWithZero_item.setHidden(False)
                self.sigmaWithZero_item.setHidden(False)
                self.muWithZero_item.setHidden(False)
                self.fwhmWithZero_item.setHidden(False)
                self.ynodWithZero_item.setHidden(False)

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
        if position != self.checkbox_position:
            return

        from .logicStats import universalFunctions as u
        from .logicStats import universalStats as s

        mvdx = None
          
        if position == 'left':
            mvdx = self.axes_window.formatted_mvdx_x
            final_slice_values = DosesAndPaths.final_slice_values_x
            ax = self.axes_window.ax_x
        elif position == 'right':
            mvdx = self.axes_window.formatted_mvdx_y
            final_slice_values = DosesAndPaths.final_slice_values_y
            ax = self.axes_window.ax_y

        #if mvdx is None:
        #    mvdx = np.arange(0, len(final_slice_values))

        if self.gauss_checked:
            v = s(np.array([mvdx, final_slice_values]), u.gauss, basisFormatter=DosesAndPaths.basis_formatter)
            v.run()
            cfs, errs = v.getMeDataForPrinting()
            try:
                self.constant_item.setText(1, f"{cfs[0]:.3f} ± {errs[0]:.3f}")
                self.mu_item.setText(1, f"{cfs[1]:.3f} ± {errs[1]:.3f}")
                self.sigma_item.setText(1, f"{cfs[2]:.3f} ± {errs[2]:.3f}")
                self.fwhm_item.setText(1, f"{cfs[3]:.3f} ± {errs[3]:.3f}")
            except:
                pass
            self.plot_additional_data(ax, v)

        if self.gaussWithZero_checked:
            v = s(np.array([mvdx, final_slice_values]), u.gaussWithZero, basisFormatter=DosesAndPaths.basis_formatter)
            v.run()
            cfs, errs = v.getMeDataForPrinting()
            self.constantWithZero_item.setText(1, f"{cfs[0]:.3f} ± {errs[0]:.3f}")
            self.muWithZero_item.setText(1, f"{cfs[1]:.3f} ± {errs[1]:.3f}")
            self.sigmaWithZero_item.setText(1, f"{cfs[2]:.3f} ± {errs[2]:.3f}")
            self.ynodWithZero_item.setText(1, f"{cfs[3]:.3f} ± {errs[3]:.3f}")
            self.fwhmWithZero_item.setText(1, f"{cfs[4]:.3f} ± {errs[4]:.3f}")
            cfs, errs = v.getMeDataForPrinting()
            self.plot_additional_data(ax, v)

        if self.poly_checked:
            v = s(np.array([mvdx, final_slice_values]), u.polynomial, basisFormatter=DosesAndPaths.basis_formatter)
            v.run()
            cfs = v.getMeDataForPrinting()
            self.cf_items[0].setText(1, f"{cfs[0]:.4f}")
            self.cf_items[1].setText(1, f"{cfs[1]:.4e}")
            self.cf_items[2].setText(1, f"{cfs[2]:.4e}")
            self.cf_items[3].setText(1, f"{cfs[3]:.4e}")
            self.plot_additional_data(ax, v)

        v = s(np.array([mvdx, final_slice_values]), u.basic, basisFormatter=DosesAndPaths.basis_formatter)
        v.run()
        self.median_item.setText(1, f"{v.getMeDataForPrinting()[3]:.1f}")
        self.mean_item.setText(1, f"{v.getMeDataForPrinting()[2]:.4f}")
        self.max_item.setText(1, f"{v.getMeDataForPrinting()[1]:.2f}")
        self.min_item.setText(1, f"{v.getMeDataForPrinting()[0]:.2f}")

    def mm_to_pixels(self, value):
        """
        Utility function for converting millimeters to pixels.
        :param value: The value in millimeters to convert to pixels
        :return: The converted value in pixels
        """
        return round(value / DosesAndPaths.basis_formatter, 0)

    def plot_additional_data(self, ax, v, color="r"):
        """
        Function for plotting additional data on a given axis.
        :param ax: The axis on which to plot the data
        :param v: object of our current fitting state  
        :type v: logicStats.universalStats
        :param cfs: The y values of the data to plot
        :param color: The color of the line to plot. Default is red.
        """
        # Check if line exists and update data
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
                #self.line_x, = ax.plot(o[0], o[1], color)
            elif ax == self.axes_window.ax_y:
                self.line_y, = ax.plot(*o)
                #self.line_y, = ax.plot(o[0], o[1], color)

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
