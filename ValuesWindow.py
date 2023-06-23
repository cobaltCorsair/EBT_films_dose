from PyQt5 import QtWidgets
from Values import Ui_Form as Values_form

class ValuesWindow(QtWidgets.QWidget, Values_form):
    """
    Class of the dialog window with a values
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)