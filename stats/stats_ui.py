from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt
from doses_and_pathes import DosesAndPaths
from stats import logicStats


class PanelWindow(QWidget):
    def __init__(self, main_window):
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

        self.tree.itemChanged.connect(self.handleItemChanged)
        self.tree.itemChanged.connect(self.on_item_changed)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tree)

        self.main_window = main_window

    def handleItemChanged(self, item, column):
        if column == 0:
            hidden = item.checkState(0) == Qt.Unchecked
            if item == self.gauss_item:
                self.constant_item.setHidden(hidden)
                self.sigma_item.setHidden(hidden)
                self.mu_item.setHidden(hidden)
            elif item == self.poly_item:
                for cf_item in self.cf_items:
                    cf_item.setHidden(hidden)

    def on_item_changed(self, item, column):
        if item == self.gauss_item and column == 0:
            if item.checkState(0) == Qt.Checked:
                print('check')
                if DosesAndPaths.final_formatted_mvdx_x is not None and self.main_window.position == 'left':
                    print(logicStats.prepareGaussOwnX(DosesAndPaths.final_formatted_mvdx_x,
                                                      DosesAndPaths.final_slice_values_x))
                if DosesAndPaths.final_formatted_mvdx_y is not None and self.main_window.position == 'right':
                    print(logicStats.prepareGaussOwnX(DosesAndPaths.final_formatted_mvdx_y,
                                                      DosesAndPaths.final_slice_values_y))
            else:
                print('uncheck')


class MainWindow(QWidget):
    def __init__(self, button, position='right'):
        super(MainWindow, self).__init__()
        self.panel = PanelWindow(self)
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
