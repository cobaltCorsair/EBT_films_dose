from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt


class PanelWindow(QWidget):
    def __init__(self):
        super(PanelWindow, self).__init__()
        self.setFixedWidth(200)  # Set the width of the panel
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

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tree)

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


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.button = QPushButton(">>", self)
        self.button.clicked.connect(self.togglePanel)

        self.panel = PanelWindow()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.button)

        self.panel.hide()

    def togglePanel(self):
        if self.panel.isHidden():
            self.panel.move(self.frameGeometry().topRight())  # Move the panel to the right of the main window
            self.panel.show()
            self.button.setText("<<")
        else:
            self.panel.hide()
            self.button.setText(">>")


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
