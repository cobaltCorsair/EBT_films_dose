# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Dose.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1099, 617)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.pushButton_8 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_8.setObjectName("pushButton_8")
        self.verticalLayout_10.addWidget(self.pushButton_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.pushButton_9 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_9.setObjectName("pushButton_9")
        self.horizontalLayout_9.addWidget(self.pushButton_9)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_9.addWidget(self.pushButton_2)
        self.verticalLayout_10.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_5.addLayout(self.verticalLayout_10)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_8.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_8.addWidget(self.pushButton)
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_8.addWidget(self.checkBox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_10.addWidget(self.lineEdit_3)
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setObjectName("pushButton_7")
        self.horizontalLayout_10.addWidget(self.pushButton_7)
        self.verticalLayout_4.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_5.addLayout(self.verticalLayout_4)
        self.horizontalLayout_5.setStretch(1, 10)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_3.addWidget(self.line_3)
        self.verticalLayout_7.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.setStretch(0, 10)
        self.horizontalLayout_3.setStretch(2, 10)
        self.verticalLayout_7.addLayout(self.horizontalLayout_3)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_7.addWidget(self.line_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_4.addWidget(self.pushButton_4)
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setObjectName("checkBox_3")
        self.horizontalLayout_4.addWidget(self.checkBox_3)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setMaximum(300)
        self.spinBox.setValue(150)
        self.spinBox.setMinimum(50)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_4.addWidget(self.spinBox)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_4.addWidget(self.comboBox)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_4.addWidget(self.pushButton_3)
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_4.addWidget(self.pushButton_6)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_4.addWidget(self.pushButton_5)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_4.addWidget(self.progressBar)
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.horizontalLayout_4.addWidget(self.checkBox_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_7.addWidget(self.label_2)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout_7.addWidget(self.doubleSpinBox)
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_7.addWidget(self.line_4)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_7.addWidget(self.label_3)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.horizontalLayout_7.addWidget(self.doubleSpinBox_2)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout_4.addLayout(self.horizontalLayout_6)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.verticalLayout_7.setStretch(1, 10)
        self.horizontalLayout.addLayout(self.verticalLayout_7)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_from_JSON_file = QtWidgets.QAction(MainWindow)
        self.actionLoad_from_JSON_file.setObjectName("actionLoad_from_JSON_file")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_8.setText(_translate("MainWindow", "Change calibration list"))
        self.pushButton_9.setText(_translate("MainWindow", "Load from file"))
        self.pushButton_2.setText(_translate("MainWindow", "DB and Settings"))
        self.pushButton.setText(_translate("MainWindow", "Unexsposed film"))
        self.checkBox.setText(_translate("MainWindow", "Use first film from calibration"))
        self.pushButton_7.setText(_translate("MainWindow", "Exposed film"))
        self.pushButton_4.setText(_translate("MainWindow", "Calculate dose"))
        self.checkBox_3.setText(_translate("MainWindow", "OD\'s only"))
        self.label.setText(_translate("MainWindow", "DPI:"))
        self.label_4.setText(_translate("MainWindow", "Filter:"))
        self.pushButton_3.setText(_translate("MainWindow", "Crop film by highlight"))
        self.pushButton_6.setText(_translate("MainWindow", "Normalize by Zone"))
        self.pushButton_5.setText(_translate("MainWindow", "Get dose by .xlsx"))
        self.checkBox_2.setText(_translate("MainWindow", "Use custom vmin/vmax"))
        self.label_2.setText(_translate("MainWindow", "vmin"))
        self.label_3.setText(_translate("MainWindow", "vmax"))
        self.actionLoad_from_JSON_file.setText(_translate("MainWindow", "Load from JSON file"))
