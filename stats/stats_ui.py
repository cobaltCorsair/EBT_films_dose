from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from doses_and_pathes import DosesAndPaths
from stats import logicStats


class PanelWindow(QWidget):
    def __init__(self, main_window, axes_window, position='right'):
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

        self.tree.itemChanged.connect(self.handleItemChanged)

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

    def handleItemChanged(self, item, column):
        if column == 0:
            hidden = item.checkState(0) == Qt.Unchecked
            if item == self.gauss_item:
                self.gauss_checked = not hidden  # обновляем состояние
                if hidden:
                    if self.position == 'left' and self.dataChangedLeftConnected:
                        self.dataChangedLeft.disconnect(self.handle_data_changed)
                        self.dataChangedLeftConnected = False
                    elif self.position == 'right' and self.dataChangedRightConnected:
                        self.dataChangedRight.disconnect(self.handle_data_changed)
                        self.dataChangedRightConnected = False
                elif not hidden:
                    if self.position == 'left':
                        self.dataChangedLeft.connect(self.handle_data_changed)
                        self.dataChangedLeftConnected = True
                    elif self.position == 'right':
                        self.dataChangedRight.connect(self.handle_data_changed)
                        self.dataChangedRightConnected = True
                    self.handle_data_changed(self.position)

    def handle_data_changed(self, position):
        # Если флажок gauss_item не установлен, не обрабатывайте данные
        if not self.gauss_checked or position != self.checkbox_position:
            print(f'Ignoring data for {position} as checkbox is not checked')
            return

        if position == 'left':
            #cfs, errs = logicStats.prepareGaussOwnX(self.axes_window.formatted_mvdx_x,
                                                    #DosesAndPaths.final_slice_values_x)
            # Call plot_additional_data with your data and the corresponding axes
            #self.plot_additional_data(self.axes_window.ax_x, self.axes_window.formatted_mvdx_x, cfs, color='r')
            print('Processing data for', position)
        if position == 'right':
            #cfs, errs = logicStats.prepareGaussOwnX(self.axes_window.formatted_mvdx_y,
                                                    #DosesAndPaths.final_slice_values_y)
            # Call plot_additional_data with your data and the corresponding axes
            #self.plot_additional_data(self.axes_window.ax_y, self.axes_window.formatted_mvdx_y, cfs, color='r')
            print('Processing data for', position)

    def plot_additional_data(self, ax, x_data, cfs, color='r'):
        """
        Plot additional data on the given axes
        :param ax: axes object where the data will be plotted
        :param x_data: x values of the data to plot
        :param cfs: y values of the data to plot
        :param color: color of the line to plot
        """
        # Check if line exists and update data
        if self.line_x is not None and ax == self.axes_window.ax_x:
            self.line_x.set_xdata(x_data)
            self.line_x.set_ydata(logicStats.gauss(x_data, *cfs))
        elif self.line_y is not None and ax == self.axes_window.ax_y:
            self.line_y.set_xdata(x_data)
            self.line_y.set_ydata(logicStats.gauss(x_data, *cfs))
        else:  # Line does not exist, create it
            if ax == self.axes_window.ax_x:
                self.line_x, = ax.plot(x_data, logicStats.gauss(x_data, *cfs), color=color)
            elif ax == self.axes_window.ax_y:
                self.line_y, = ax.plot(x_data, logicStats.gauss(x_data, *cfs), color=color)

        ax.figure.canvas.draw()


class MainWindow(QWidget):
    def __init__(self, button, axes_window, position='right'):
        super(MainWindow, self).__init__()
        self.panel = PanelWindow(self, axes_window=axes_window, position=position)
        self.panel.setWindowTitle("Stats " + ('Y' if position == 'right' else 'X'))
        self.panel.hide()

        self.button = button
        self.position = position

    def show_panel(self):
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
