from PyQt5 import QtWidgets
from FileDialog import MyQFileDialog
from ui.calibrate_list import Ui_Form
from SaveLoadData import SaveLoadData
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QLineEdit, QDoubleSpinBox
from DosesAndPaths import DosesAndPaths
from Warnings import Warnings
from CurveWindow import CurveWindow
from ValuesWindow import ValuesWindow

application = None

class Form(QtWidgets.QWidget, Ui_Form):
    """
    UI class for displaying dose/path list
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.widget_count = 0
        self.all_widgets = None
        self.curve_win = None
        self.value_win = None

        self.pushButton_5.setDisabled(True)
        self.pushButton_9.setDisabled(True)

        self.pushButton.clicked.connect(lambda: self.get_empty_field_file(self.lineEdit))
        self.pushButton_2.clicked.connect(self.dynamic_add_fields)
        self.pushButton_3.clicked.connect(self.dynamic_delete_fields)
        self.pushButton_4.clicked.connect(self.get_all_params_widgets)
        self.pushButton_5.clicked.connect(self.draw_curve)
        self.pushButton_8.clicked.connect(SaveLoadData.create_json)
        self.pushButton_6.clicked.connect(lambda: self.get_empty_field_file(self.lineEdit_2))
        self.pushButton_9.clicked.connect(self.get_values)

    def search_file(self):
        """
        Search file
        """
        file_name = MyQFileDialog.getOpenFileName(
            parent=self,
            caption='Open file',
            filter='*.tif',
            options=QFileDialog.DontUseNativeDialog
        )[0]
        return file_name

    def get_empty_field_file(self, line):
        """Set the found file in lineEdit"""
        line.setText(self.search_file())

        if len(line.text()) != 0:
            line.setDisabled(True)

    def dynamic_add_fields(self):
        """
        Dynamically adding fields to record new paths/doses
        """
        spin_box = QtWidgets.QDoubleSpinBox()
        qline_edit = QtWidgets.QLineEdit()
        push_button = QtWidgets.QPushButton("Select")
        checkbox = QtWidgets.QCheckBox()

        self.gridLayout_3.addWidget(checkbox)
        self.gridLayout_3.addWidget(spin_box)
        self.gridLayout_3.addWidget(qline_edit)
        self.gridLayout_3.addWidget(push_button)

        push_button.clicked.connect(lambda: self.get_empty_field_file(qline_edit))

        self.widget_count += 1
        self.adjustSize()

    def dynamic_delete_fields(self):
        """
        Deleting fields to record paths/doses
        """
        widgets = [self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count())]
        checkboxes = [i for i in widgets if isinstance(i, QCheckBox)]

        for k in checkboxes:
            if k.checkState() == 2:
                index = widgets.index(k)
                for j in range(4):
                    my_widget = self.gridLayout_3.itemAt(index).widget()
                    my_widget.setParent(None)
                    self.adjustSize()
                    widgets.remove(my_widget)

    def get_all_params_widgets(self):
        """
        Set values from fields to variables
        """
        doses = []
        paths = []
        sigma = self.spinBox.value()
        widgets = (self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count()))
        self.all_widgets = widgets
        for widget in widgets:
            if isinstance(widget, QLineEdit):
                paths.append(widget.text())
            if isinstance(widget, QDoubleSpinBox):
                doses.append(widget.value())
            if isinstance(widget, QLineEdit) and widget.text() is '':
                Warnings.error_empty_value()

        DosesAndPaths.doses = doses
        DosesAndPaths.paths = paths
        DosesAndPaths.sigma = sigma
        DosesAndPaths.fit_func_type = self.comboBox.currentText()
        DosesAndPaths.empty_scanner_field_file = self.lineEdit_2.text()
        DosesAndPaths.calculation_doses.clear()

        self.get_enabled_curve_drawing()
        #CalcUI.HAND_SWITCH_MODE = True
        application.HAND_SWITCH_MODE = True

    def get_enabled_curve_drawing(self):
        """
        Blocking the availability of fields for editing
        """
        if len(DosesAndPaths.doses) is not 0 and len(DosesAndPaths.paths) is not 0:
            self.pushButton_5.setDisabled(False)

    def draw_curve(self):
        """
        The method connects methods of drawing graphs
        """
        self.curve_win = CurveWindow()
        self.curve_win.get_curve()
        self.curve_win.setMinimumSize(640, 480)
        self.curve_win.show()
        self.pushButton_5.setDisabled(True)
        self.pushButton_9.setDisabled(False)

    def create_widgets_second_open(self):
        """
        The method restores the fields created by the user when the window is reopened
        """
        data_count = len(DosesAndPaths.doses)
        if self.gridLayout_3.count() >= 6 and data_count > 1:
            for i in range(data_count - 1):
                self.dynamic_add_fields()

    def insert_data_in_fields(self):
        """
        Fill in the dialog window with doses and paths when opening
        """
        widgets = [self.gridLayout_3.itemAt(i).widget() for i in range(self.gridLayout_3.count())]
        lineedits = [i for i in widgets if isinstance(i, QLineEdit)]
        spinboxes = [i for i in widgets if isinstance(i, QDoubleSpinBox)]

        for path, dose, line, spin in zip(DosesAndPaths.paths, DosesAndPaths.doses, lineedits, spinboxes):
            if isinstance(line, QLineEdit):
                line.setText(path)
            if isinstance(spin, QDoubleSpinBox):
                spin.setValue((float(dose)))

        self.spinBox.setValue(DosesAndPaths.sigma)
        self.lineEdit_2.setText(DosesAndPaths.empty_scanner_field_file)
        self.comboBox.setCurrentText(DosesAndPaths.fit_func_type)

    def get_values(self):
        """
        Get the values of doses, calculation doses and p_opt in dialog window
        """
        self.value_win = ValuesWindow()
        if len(DosesAndPaths.calculation_doses) > 0:
            self.value_win.plainTextEdit.appendPlainText(
                ('DOSES: \n' + ('\n'.join(map(str, [round(x, 4) for x in DosesAndPaths.doses]))).replace('.', ',')))
            self.value_win.plainTextEdit.appendPlainText(('\nOPTICAL DENSITY: \n' + (
                '\n'.join(map(str, [round(x, 4) for x in DosesAndPaths.calculation_doses]))).replace('.', ',')))
            self.value_win.plainTextEdit.appendPlainText(('\nPOLY_COEF_A_B_C: \n' + (
                '\n'.join(map(str, [round(x, 4) for x in DosesAndPaths.p_opt]))).replace('.', ',')))
        self.value_win.show()



