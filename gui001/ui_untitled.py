# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitlednmLvYS.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1004, 660)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(-60, -40, 1121, 721))
        self.label.setPixmap(QPixmap(u"res/background.png"))
        self.label.setScaledContents(True)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(70, 50, 921, 581))
        self.tabWidget.setStyleSheet(u"QTabWidget::pane{\n"
"min-width:70px;\n"
"min-height:25px;\n"
"border-top: 1px solid;\n"
"\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"\n"
"min-width:70px;\n"
"\n"
"min-height:25px;\n"
"\n"
"color: white;\n"
"\n"
"font:15px \"Microsoft YaHei\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"\n"
"\n"
"}\n"
"\n"
"QTabBar::tab:selected{\n"
"\n"
"min-width:70px;\n"
"\n"
"min-height:25px;\n"
"color: white;\n"
"\n"
"font:16px \"Microsoft YaHei\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"border-bottom: 1px solid;\n"
"\n"
"border-color: #4796f0\n"
";\n"
"\n"
"}")
        self.tabWidget.setIconSize(QSize(20, 16))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget_3 = QTabWidget(self.tab)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.tabWidget_3.setGeometry(QRect(20, 0, 881, 541))
        self.tabWidget_3.setStyleSheet(u"QTabWidget::pane{\n"
"min-width:70px;\n"
"min-height:25px;\n"
"border-top: 1px solid;\n"
"\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"\n"
"min-width:70px;\n"
"\n"
"min-height:25px;\n"
"\n"
"color: white;\n"
"\n"
"font:14px \"Microsoft YaHei\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"\n"
"\n"
"}\n"
"\n"
"QTabBar::tab:selected{\n"
"\n"
"min-width:70px;\n"
"\n"
"min-height:25px;\n"
"color: white;\n"
"\n"
"font:15px \"Microsoft YaHei\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"border-bottom: 1px solid;\n"
"\n"
"border-color: #4796f0;\n"
"\n"
"}")
        self.tab_9 = QWidget()
        self.tab_9.setObjectName(u"tab_9")
        self.lineEdit = QLineEdit(self.tab_9)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(0, 20, 91, 31))
        self.lineEdit.setStyleSheet(u"background-color: rgb(49, 54, 98);\n"
"font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"color:white;")
        self.pushButton = QPushButton(self.tab_9)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(80, 20, 111, 31))
        self.pushButton.setStyleSheet(u"QPushButton {	\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border-image: url(:/newPrefix/search_button.png);\n"
"}\n"
"QPushButton:hover {\n"
"	border-image: url(:/newPrefix/search_button_2.png);\n"
"}\n"
"QPushButton:pressed {	\n"
"	border-image: url(:/newPrefix/search_button.png);\n"
"}\n"
"")
        icon = QIcon()
        icon.addFile(u"res/camera.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QSize(29, 31))
        self.btn_open_camera = QPushButton(self.tab_9)
        self.btn_open_camera.setObjectName(u"btn_open_camera")
        self.btn_open_camera.setGeometry(QRect(150, 70, 151, 31))
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_open_camera.sizePolicy().hasHeightForWidth())
        self.btn_open_camera.setSizePolicy(sizePolicy)
        self.btn_open_camera.setMinimumSize(QSize(0, 0))
        self.btn_open_camera.setMaximumSize(QSize(16777215, 16777215))
        self.btn_open_camera.setStyleSheet(u"QPushButton {	\n"
"	color:white;\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border: 1px solid #A7A8B6;\n"
"	background-color:transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color:transparent;\n"
"	border: 1px solid #FFFFFF;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.btn_capture_frame = QPushButton(self.tab_9)
        self.btn_capture_frame.setObjectName(u"btn_capture_frame")
        self.btn_capture_frame.setGeometry(QRect(570, 70, 151, 31))
        sizePolicy.setHeightForWidth(self.btn_capture_frame.sizePolicy().hasHeightForWidth())
        self.btn_capture_frame.setSizePolicy(sizePolicy)
        self.btn_capture_frame.setMinimumSize(QSize(0, 0))
        self.btn_capture_frame.setMaximumSize(QSize(16777215, 16777215))
        self.btn_capture_frame.setStyleSheet(u"QPushButton {	\n"
"	color:white;\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border: 1px solid #A7A8B6;\n"
"	background-color:transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color:transparent;\n"
"	border: 1px solid #FFFFFF;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.camera = QLabel(self.tab_9)
        self.camera.setObjectName(u"camera")
        self.camera.setGeometry(QRect(70, 130, 321, 331))
        self.photo = QLabel(self.tab_9)
        self.photo.setObjectName(u"photo")
        self.photo.setGeometry(QRect(480, 130, 321, 331))
        self.label_20 = QLabel(self.tab_9)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setGeometry(QRect(70, 130, 321, 331))
        self.label_20.setStyleSheet(u"")
        self.label_20.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.label_21 = QLabel(self.tab_9)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setGeometry(QRect(480, 130, 321, 331))
        self.label_21.setStyleSheet(u"")
        self.label_21.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.tabWidget_3.addTab(self.tab_9, "")
        self.tab_10 = QWidget()
        self.tab_10.setObjectName(u"tab_10")
        self.label_4 = QLabel(self.tab_10)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(110, 60, 61, 51))
        self.label_4.setPixmap(QPixmap(u"res/slideshow.png"))
        self.label_4.setScaledContents(True)
        self.btn_open_image = QPushButton(self.tab_10)
        self.btn_open_image.setObjectName(u"btn_open_image")
        self.btn_open_image.setGeometry(QRect(70, 110, 141, 31))
        sizePolicy.setHeightForWidth(self.btn_open_image.sizePolicy().hasHeightForWidth())
        self.btn_open_image.setSizePolicy(sizePolicy)
        self.btn_open_image.setMinimumSize(QSize(0, 0))
        self.btn_open_image.setMaximumSize(QSize(16777215, 16777215))
        self.btn_open_image.setStyleSheet(u"QPushButton {	\n"
"	color:white;\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border: 1px solid #A7A8B6;\n"
"	background-color:transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color:transparent;\n"
"	border: 1px solid #FFFFFF;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.image = QLabel(self.tab_10)
        self.image.setObjectName(u"image")
        self.image.setGeometry(QRect(320, 40, 471, 441))
        self.image.setStyleSheet(u"")
        self.image.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.image_board = QLabel(self.tab_10)
        self.image_board.setObjectName(u"image_board")
        self.image_board.setGeometry(QRect(323, 41, 471, 441))
        self.tabWidget_3.addTab(self.tab_10, "")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget_2 = QTabWidget(self.tab_2)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tabWidget_2.setGeometry(QRect(20, 0, 881, 551))
        self.tabWidget_2.setStyleSheet(u"QTabWidget::pane{\n"
"min-width:70px;\n"
"min-height:25px;\n"
"border-top: 1px solid;\n"
"\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"\n"
"min-width:70px;\n"
"\n"
"min-height:25px;\n"
"\n"
"color: white;\n"
"\n"
"font:14px \"Microsoft YaHei\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"\n"
"\n"
"}\n"
"\n"
"QTabBar::tab:selected{\n"
"\n"
"min-width:70px;\n"
"\n"
"min-height:25px;\n"
"color: white;\n"
"\n"
"font:15px \"Microsoft YaHei\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"border-bottom: 1px solid;\n"
"\n"
"border-color: #4796f0;\n"
"\n"
"}")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.btn_meter_ocr = QPushButton(self.tab_3)
        self.btn_meter_ocr.setObjectName(u"btn_meter_ocr")
        self.btn_meter_ocr.setGeometry(QRect(110, 100, 151, 51))
        sizePolicy.setHeightForWidth(self.btn_meter_ocr.sizePolicy().hasHeightForWidth())
        self.btn_meter_ocr.setSizePolicy(sizePolicy)
        self.btn_meter_ocr.setMinimumSize(QSize(0, 0))
        self.btn_meter_ocr.setMaximumSize(QSize(16777215, 16777215))
        self.btn_meter_ocr.setStyleSheet(u"QPushButton {	\n"
"	font: 10pt \"\u6977\u4f53\";\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border-image: url(:/newPrefix/button2.png);\n"
"}\n"
"QPushButton:hover {\n"
"	border-image: url(:/newPrefix/button.png);\n"
"}\n"
"QPushButton:pressed {	\n"
"	border-image: url(:/newPrefix/button2.png);\n"
"}")
        self.pushButton_4 = QPushButton(self.tab_3)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(20, 460, 51, 51))
        self.pushButton_4.setStyleSheet(u"QPushButton{\n"
"	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:0, 		stop:0.1 rgba(85, 170, 255, 255), stop:0.09 rgba(255, 255, 255, 255));\n"
"	border-radius: 25px;\n"
"	border: 2px solid gray;\n"
"}\n"
"QPushButton:hover{                    \n"
"	border:2px solid gray;\n"
"}\n"
"QPushButton:pressed{\n"
"	border: 2px solid gray;\n"
"}")
        self.label_8 = QLabel(self.tab_3)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(30, 420, 81, 31))
        self.label_8.setStyleSheet(u"color:white;\n"
"font: 11pt \"AcadEref\";\n"
"font-family:\u5fae\u8f6f\u96c5\u9ed1;")
        self.label_5 = QLabel(self.tab_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(80, 70, 51, 61))
        self.label_5.setPixmap(QPixmap(u"res/\u89e6\u5c4f.png"))
        self.label_5.setScaledContents(True)
        self.label_7 = QLabel(self.tab_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(430, 20, 421, 491))
        self.label_7.setStyleSheet(u"background-color: rgb(85, 85, 127);")
        self.text_meterocr = QTextEdit(self.tab_3)
        self.text_meterocr.setObjectName(u"text_meterocr")
        self.text_meterocr.setGeometry(QRect(450, 40, 381, 451))
        self.btn_screen_information = QPushButton(self.tab_3)
        self.btn_screen_information.setObjectName(u"btn_screen_information")
        self.btn_screen_information.setGeometry(QRect(110, 290, 151, 51))
        sizePolicy.setHeightForWidth(self.btn_screen_information.sizePolicy().hasHeightForWidth())
        self.btn_screen_information.setSizePolicy(sizePolicy)
        self.btn_screen_information.setMinimumSize(QSize(0, 0))
        self.btn_screen_information.setMaximumSize(QSize(16777215, 16777215))
        self.btn_screen_information.setStyleSheet(u"QPushButton {	\n"
"	font: 10pt \"\u6977\u4f53\";\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border-image: url(:/newPrefix/button2.png);\n"
"}\n"
"QPushButton:hover {\n"
"	border-image: url(:/newPrefix/button.png);\n"
"}\n"
"QPushButton:pressed {	\n"
"	border-image: url(:/newPrefix/button2.png);\n"
"}")
        self.label_6 = QLabel(self.tab_3)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(80, 260, 51, 61))
        self.label_6.setPixmap(QPixmap(u"res/\u89e6\u5c4f.png"))
        self.label_6.setScaledContents(True)
        self.label_16 = QLabel(self.tab_3)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(0, 0, 511, 521))
        self.label_16.setStyleSheet(u"")
        self.label_16.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.label_18 = QLabel(self.tab_3)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(510, 0, 381, 521))
        self.label_18.setStyleSheet(u"")
        self.label_18.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.tabWidget_2.addTab(self.tab_3, "")
        self.label_16.raise_()
        self.label_18.raise_()
        self.label_7.raise_()
        self.btn_meter_ocr.raise_()
        self.pushButton_4.raise_()
        self.label_8.raise_()
        self.label_5.raise_()
        self.text_meterocr.raise_()
        self.btn_screen_information.raise_()
        self.label_6.raise_()
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.label_14 = QLabel(self.tab_4)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(820, 470, 31, 31))
        self.label_14.setStyleSheet(u"")
        self.label_14.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/yx.png"))
        self.label_15 = QLabel(self.tab_4)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(350, 470, 31, 31))
        self.label_15.setStyleSheet(u"")
        self.label_15.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/zx.png"))
        self.label_13 = QLabel(self.tab_4)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(350, 19, 31, 31))
        self.label_13.setStyleSheet(u"")
        self.label_13.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/zs.png"))
        self.label_12 = QLabel(self.tab_4)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(820, 20, 31, 31))
        self.label_12.setStyleSheet(u"")
        self.label_12.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/ys.png"))
        self.label_10 = QLabel(self.tab_4)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(340, 10, 531, 501))
        self.label_10.setStyleSheet(u"")
        self.label_10.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.label_11 = QLabel(self.tab_4)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(360, 30, 481, 461))
        self.label_11.setStyleSheet(u"")
        self.label_11.setPixmap(QPixmap(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/bk.png"))
        self.label_9 = QLabel(self.tab_4)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(0, 250, 311, 171))
        self.label_9.setStyleSheet(u"font: 28pt \"\u96b6\u4e66\";\n"
"color: rgb(0, 170, 255);")
        self.text_data_ocr = QTextEdit(self.tab_4)
        self.text_data_ocr.setObjectName(u"text_data_ocr")
        self.text_data_ocr.setGeometry(QRect(370, 40, 461, 441))
        self.label_17 = QLabel(self.tab_4)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(30, 70, 51, 61))
        self.label_17.setPixmap(QPixmap(u"res/\u89e6\u5c4f.png"))
        self.label_17.setScaledContents(True)
        self.btn_historical_data = QPushButton(self.tab_4)
        self.btn_historical_data.setObjectName(u"btn_historical_data")
        self.btn_historical_data.setGeometry(QRect(60, 100, 151, 51))
        sizePolicy.setHeightForWidth(self.btn_historical_data.sizePolicy().hasHeightForWidth())
        self.btn_historical_data.setSizePolicy(sizePolicy)
        self.btn_historical_data.setMinimumSize(QSize(0, 0))
        self.btn_historical_data.setMaximumSize(QSize(16777215, 16777215))
        self.btn_historical_data.setStyleSheet(u"QPushButton {	\n"
"	font: 10pt \"\u6977\u4f53\";\n"
"	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
"	border-image: url(:/newPrefix/button2.png);\n"
"}\n"
"QPushButton:hover {\n"
"	border-image: url(:/newPrefix/button.png);\n"
"}\n"
"QPushButton:pressed {	\n"
"	border-image: url(:/newPrefix/button2.png);\n"
"}")
        self.tabWidget_2.addTab(self.tab_4, "")
        self.label_10.raise_()
        self.label_11.raise_()
        self.label_9.raise_()
        self.text_data_ocr.raise_()
        self.label_12.raise_()
        self.label_14.raise_()
        self.label_13.raise_()
        self.label_15.raise_()
        self.btn_historical_data.raise_()
        self.label_17.raise_()
        self.tabWidget.addTab(self.tab_2, "")
        self.btn_close = QPushButton(self.centralwidget)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setGeometry(QRect(950, 10, 40, 51))
        sizePolicy.setHeightForWidth(self.btn_close.sizePolicy().hasHeightForWidth())
        self.btn_close.setSizePolicy(sizePolicy)
        self.btn_close.setMinimumSize(QSize(20, 0))
        self.btn_close.setMaximumSize(QSize(40, 16777215))
        self.btn_close.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	border-radius: 6px;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(38, 43, 85);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: transparent;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/24gl-extractLeft.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_close.setIcon(icon1)
        self.btn_minimize = QPushButton(self.centralwidget)
        self.btn_minimize.setObjectName(u"btn_minimize")
        self.btn_minimize.setGeometry(QRect(910, 10, 31, 51))
        sizePolicy.setHeightForWidth(self.btn_minimize.sizePolicy().hasHeightForWidth())
        self.btn_minimize.setSizePolicy(sizePolicy)
        self.btn_minimize.setMinimumSize(QSize(20, 0))
        self.btn_minimize.setMaximumSize(QSize(40, 16777215))
        self.btn_minimize.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	border-radius: 6px;\n"
"	background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(38, 43, 85);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: transparent;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u"../../../pyqt5/Bilibili\u6587\u4ef6\u6e90\u7801 + \u8d44\u6e90/CSGO_\u4effB5\u5e73\u53f0\u754c\u9762/res/\u6700\u5c0f\u5316.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_minimize.setIcon(icon2)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 0, 81, 81))
        self.label_2.setPixmap(QPixmap(u"res/logo.png"))
        self.label_2.setScaledContents(True)
        self.label_welcome = QLabel(self.centralwidget)
        self.label_welcome.setObjectName(u"label_welcome")
        self.label_welcome.setGeometry(QRect(260, 10, 381, 51))
        self.label_welcome.setStyleSheet(u"font: 15pt \"\u534e\u6587\u96b6\u4e66\";\n"
"color: rgb(255, 170, 0);")
        self.label_time = QLabel(self.centralwidget)
        self.label_time.setObjectName(u"label_time")
        self.label_time.setGeometry(QRect(620, 10, 241, 51))
        self.label_time.setStyleSheet(u"font: 15pt \"\u534e\u6587\u96b6\u4e66\";\n"
"color: rgb(255, 170, 0);")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(1)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText("")
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u5b9e\u65f6\u62cd\u6444", None))
#if QT_CONFIG(tooltip)
        self.btn_open_camera.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_open_camera.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u6444\u50cf\u5934", None))
#if QT_CONFIG(tooltip)
        self.btn_capture_frame.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_capture_frame.setText(QCoreApplication.translate("MainWindow", u"\u6355\u83b7\u5e27", None))
        self.camera.setText("")
        self.photo.setText("")
        self.label_20.setText("")
        self.label_21.setText("")
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_9), QCoreApplication.translate("MainWindow", u"Camera", None))
        self.label_4.setText("")
#if QT_CONFIG(tooltip)
        self.btn_open_image.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_open_image.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u56fe\u7247", None))
        self.image.setText("")
        self.image_board.setText("")
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_10), QCoreApplication.translate("MainWindow", u"Photo", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Function", None))
#if QT_CONFIG(tooltip)
        self.btn_meter_ocr.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_meter_ocr.setText(QCoreApplication.translate("MainWindow", u"Meter OCR", None))
        self.pushButton_4.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"CPU", None))
        self.label_5.setText("")
        self.label_7.setText("")
        self.text_meterocr.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.btn_screen_information.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_screen_information.setText(QCoreApplication.translate("MainWindow", u"\u5c4f\u5e55\u4fe1\u606f", None))
        self.label_6.setText("")
        self.label_16.setText("")
        self.label_18.setText("")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Paddle", None))
        self.label_14.setText("")
        self.label_15.setText("")
        self.label_13.setText("")
        self.label_12.setText("")
        self.label_10.setText("")
        self.label_11.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u" \u611f\u8c22\u4f7f\u7528\uff01", None))
        self.text_data_ocr.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.label_17.setText("")
#if QT_CONFIG(tooltip)
        self.btn_historical_data.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_historical_data.setText(QCoreApplication.translate("MainWindow", u"\u5386\u53f2\u6570\u636e", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Text", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Identification", None))
#if QT_CONFIG(tooltip)
        self.btn_close.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_close.setText("")
#if QT_CONFIG(tooltip)
        self.btn_minimize.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize", None))
#endif // QT_CONFIG(tooltip)
        self.btn_minimize.setText("")
        self.label_2.setText("")
        self.label_welcome.setText(QCoreApplication.translate("MainWindow", u"\u6b22\u8fce\u4f7f\u7528 Meter OCR !", None))
        self.label_time.setText(QCoreApplication.translate("MainWindow", u"123433545657", None))
    # retranslateUi

