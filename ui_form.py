# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QTextEdit, QWidget)
import rc_rec

class Ui_gui(object):
    def setupUi(self, gui):
        if not gui.objectName():
            gui.setObjectName(u"gui")
        gui.resize(643, 800)
        self.centralwidget = QWidget(gui)
        self.centralwidget.setObjectName(u"centralwidget")
        self.background = QLabel(self.centralwidget)
        self.background.setObjectName(u"background")
        self.background.setGeometry(QRect(0, 0, 643, 800))
        self.background.setPixmap(QPixmap(u":/new/prefix1/jpeg/login.jpg"))
        self.background.setScaledContents(True)
        self.login_widget = QWidget(self.centralwidget)
        self.login_widget.setObjectName(u"login_widget")
        self.login_widget.setGeometry(QRect(0, 49, 643, 751))
        self.login_widget.setStyleSheet(u"\n"
"background-color: transparent;\n"
"")
        self.loginButton = QPushButton(self.login_widget)
        self.loginButton.setObjectName(u"loginButton")
        self.loginButton.setGeometry(QRect(282, 514, 153, 49))
        self.loginButton.setStyleSheet(u"\n"
"                    font: 17pt \"\u534e\u6587\u6977\u4f53\";\n"
"                ")
        self.label_2 = QLabel(self.login_widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(130, 182, 453, 475))
        self.label_2.setStyleSheet(u"background-color: rgba(254, 251, 244, 220);\n"
"\n"
"")
        self.label_Username = QLabel(self.login_widget)
        self.label_Username.setObjectName(u"label_Username")
        self.label_Username.setGeometry(QRect(158, 284, 103, 47))
        self.label_Username.setStyleSheet(u"font: 500 15pt \"\u7231\u5947\u827a\u9ed1\u4f53 Medium\";")
        self.label_Password = QLabel(self.login_widget)
        self.label_Password.setObjectName(u"label_Password")
        self.label_Password.setGeometry(QRect(160, 396, 105, 47))
        self.label_Password.setStyleSheet(u"font: 500 15pt \"\u7231\u5947\u827a\u9ed1\u4f53 Medium\";")
        self.Username_LineEdit = QLineEdit(self.login_widget)
        self.Username_LineEdit.setObjectName(u"Username_LineEdit")
        self.Username_LineEdit.setGeometry(QRect(266, 284, 285, 45))
        self.Username_LineEdit.setStyleSheet(u"font: 16pt \"\u65b9\u6b63\u7c97\u9ed1\u5b8b\u7b80\u4f53\";")
        self.Password_LineEdit = QLineEdit(self.login_widget)
        self.Password_LineEdit.setObjectName(u"Password_LineEdit")
        self.Password_LineEdit.setGeometry(QRect(266, 396, 285, 45))
        self.Password_LineEdit.setStyleSheet(u"font: 16pt \"\u65b9\u6b63\u7c97\u9ed1\u5b8b\u7b80\u4f53\";")
        self.label_2.raise_()
        self.loginButton.raise_()
        self.label_Username.raise_()
        self.label_Password.raise_()
        self.Password_LineEdit.raise_()
        self.Username_LineEdit.raise_()
        self.operator_widget = QWidget(self.centralwidget)
        self.operator_widget.setObjectName(u"operator_widget")
        self.operator_widget.setGeometry(QRect(0, 49, 643, 751))
        self.operator_widget.setStyleSheet(u"\n"
"background-color: transparent;\n"
"")
        self.label_4 = QLabel(self.operator_widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(0, 0, 643, 751))
        self.label_4.setPixmap(QPixmap(u":/new/prefix1/jpeg/background.jpg"))
        self.label_4.setScaledContents(True)
        self.btn_open_image = QPushButton(self.operator_widget)
        self.btn_open_image.setObjectName(u"btn_open_image")
        self.btn_open_image.setGeometry(QRect(102, 306, 141, 43))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_open_image.sizePolicy().hasHeightForWidth())
        self.btn_open_image.setSizePolicy(sizePolicy)
        self.btn_open_image.setMinimumSize(QSize(0, 0))
        self.btn_open_image.setMaximumSize(QSize(16777215, 16777215))
        self.btn_open_image.setStyleSheet(u"QPushButton {	\n"
"	color:black;\n"
"	font:16pt\"\u534e\u6587\u65b0\u9b4f\";\n"
"	border: 1px solid #A7A8B6;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"     background-color: rgba(244, 239, 231,180);\n"
"	border: 1px solid #726f6b;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.image_board = QLabel(self.operator_widget)
        self.image_board.setObjectName(u"image_board")
        self.image_board.setGeometry(QRect(52, 12, 246, 279))
        self.image_board.setStyleSheet(u"     background-color: rgba(244, 239, 231,120);")
        self.btn_capture_frame = QPushButton(self.operator_widget)
        self.btn_capture_frame.setObjectName(u"btn_capture_frame")
        self.btn_capture_frame.setGeometry(QRect(102, 660, 141, 43))
        sizePolicy.setHeightForWidth(self.btn_capture_frame.sizePolicy().hasHeightForWidth())
        self.btn_capture_frame.setSizePolicy(sizePolicy)
        self.btn_capture_frame.setMinimumSize(QSize(0, 0))
        self.btn_capture_frame.setMaximumSize(QSize(16777215, 16777215))
        self.btn_capture_frame.setStyleSheet(u"QPushButton {	\n"
"	color:black;\n"
"	font:16pt\"\u534e\u6587\u65b0\u9b4f\";\n"
"	border: 1px solid #A7A8B6;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"     background-color: rgba(244, 239, 231,180);\n"
"	border: 1px solid #726f6b;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.canema_save = QLabel(self.operator_widget)
        self.canema_save.setObjectName(u"canema_save")
        self.canema_save.setGeometry(QRect(52, 368, 246, 279))
        self.canema_save.setStyleSheet(u"     background-color: rgba(244, 239, 231,120);")
        self.text_meterocr_photo = QTextEdit(self.operator_widget)
        self.text_meterocr_photo.setObjectName(u"text_meterocr_photo")
        self.text_meterocr_photo.setGeometry(QRect(354, 10, 246, 279))
        self.text_meterocr_photo.setStyleSheet(u"border: none;\n"
"background-color: rgba(244, 239, 231,120);")
        self.btn_meter_ocr_photo = QPushButton(self.operator_widget)
        self.btn_meter_ocr_photo.setObjectName(u"btn_meter_ocr_photo")
        self.btn_meter_ocr_photo.setGeometry(QRect(408, 306, 141, 43))
        sizePolicy.setHeightForWidth(self.btn_meter_ocr_photo.sizePolicy().hasHeightForWidth())
        self.btn_meter_ocr_photo.setSizePolicy(sizePolicy)
        self.btn_meter_ocr_photo.setMinimumSize(QSize(0, 0))
        self.btn_meter_ocr_photo.setMaximumSize(QSize(16777215, 16777215))
        self.btn_meter_ocr_photo.setStyleSheet(u"QPushButton {	\n"
"	color:black;\n"
"	font:16pt\"\u534e\u6587\u65b0\u9b4f\";\n"
"	border: 1px solid #A7A8B6;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"     background-color: rgba(244, 239, 231,180);\n"
"	border: 1px solid #726f6b;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.text_meterocr_camera = QTextEdit(self.operator_widget)
        self.text_meterocr_camera.setObjectName(u"text_meterocr_camera")
        self.text_meterocr_camera.setGeometry(QRect(354, 368, 246, 279))
        self.text_meterocr_camera.setStyleSheet(u"border: none;\n"
"background-color: rgba(244, 239, 231,120);")
        self.btn_meter_ocr_camera = QPushButton(self.operator_widget)
        self.btn_meter_ocr_camera.setObjectName(u"btn_meter_ocr_camera")
        self.btn_meter_ocr_camera.setGeometry(QRect(408, 664, 141, 43))
        sizePolicy.setHeightForWidth(self.btn_meter_ocr_camera.sizePolicy().hasHeightForWidth())
        self.btn_meter_ocr_camera.setSizePolicy(sizePolicy)
        self.btn_meter_ocr_camera.setMinimumSize(QSize(0, 0))
        self.btn_meter_ocr_camera.setMaximumSize(QSize(16777215, 16777215))
        self.btn_meter_ocr_camera.setStyleSheet(u"QPushButton {	\n"
"	color:black;\n"
"	font:16pt\"\u534e\u6587\u65b0\u9b4f\";\n"
"	border: 1px solid #A7A8B6;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"     background-color: rgba(244, 239, 231,180);\n"
"	border: 1px solid #726f6b;\n"
"}\n"
"QPushButton:pressed {	\n"
"	border: 1px solid #A7A8B6;\n"
"}")
        self.closeButton = QPushButton(self.centralwidget)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setGeometry(QRect(592, 2, 49, 41))
        self.closeButton.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgba(255, 0, 0, 100);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: transparent;\n"
"}")
        icon = QIcon(QIcon.fromTheme(u"system-shutdown"))
        self.closeButton.setIcon(icon)
        self.closeButton.setIconSize(QSize(26, 26))
        self.minimizeButton = QPushButton(self.centralwidget)
        self.minimizeButton.setObjectName(u"minimizeButton")
        self.minimizeButton.setGeometry(QRect(543, 2, 49, 41))
        self.minimizeButton.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"     background-color: rgba(244, 239, 231,220);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: transparent;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/new/prefix1/jpeg/zuixiaohua.jpg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizeButton.setIcon(icon1)
        self.minimizeButton.setIconSize(QSize(26, 26))
        self.time_label = QLabel(self.centralwidget)
        self.time_label.setObjectName(u"time_label")
        self.time_label.setGeometry(QRect(152, 2, 291, 51))
        self.time_label.setStyleSheet(u"color: rgb(77, 77, 77);\n"
"font: 15pt \"\u6977\u4f53\";")
        self.menu_widget = QWidget(self.centralwidget)
        self.menu_widget.setObjectName(u"menu_widget")
        self.menu_widget.setGeometry(QRect(0, 49, 643, 751))
        self.menu_widget.setStyleSheet(u"\n"
"background-color: transparent;\n"
"")
        self.enroll_pushButton = QPushButton(self.menu_widget)
        self.enroll_pushButton.setObjectName(u"enroll_pushButton")
        self.enroll_pushButton.setGeometry(QRect(250, 294, 201, 53))
        self.enroll_pushButton.setStyleSheet(u"\n"
"     font: 17pt \"\u534e\u6587\u6977\u4f53\";")
        self.login_pushButton = QPushButton(self.menu_widget)
        self.login_pushButton.setObjectName(u"login_pushButton")
        self.login_pushButton.setGeometry(QRect(250, 460, 201, 53))
        self.login_pushButton.setStyleSheet(u"\n"
"                    font: 17pt \"\u534e\u6587\u6977\u4f53\";\n"
"                ")
        self.label = QLabel(self.menu_widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(130, 182, 453, 475))
        self.label.setStyleSheet(u"background-color: rgba(254, 251, 244, 220);\n"
"\n"
"")
        self.label.raise_()
        self.enroll_pushButton.raise_()
        self.login_pushButton.raise_()
        self.enroll_widget = QWidget(self.centralwidget)
        self.enroll_widget.setObjectName(u"enroll_widget")
        self.enroll_widget.setGeometry(QRect(0, 49, 643, 751))
        self.enroll_widget.setStyleSheet(u"\n"
"background-color: transparent;\n"
"")
        self.enrollButton = QPushButton(self.enroll_widget)
        self.enrollButton.setObjectName(u"enrollButton")
        self.enrollButton.setGeometry(QRect(282, 554, 153, 49))
        self.enrollButton.setStyleSheet(u"\n"
"     font: 17pt \"\u534e\u6587\u6977\u4f53\";")
        self.label_3 = QLabel(self.enroll_widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(130, 172, 453, 485))
        self.label_3.setStyleSheet(u"background-color: rgba(254, 251, 244, 220);\n"
"\n"
"")
        self.label_password = QLabel(self.enroll_widget)
        self.label_password.setObjectName(u"label_password")
        self.label_password.setGeometry(QRect(160, 348, 115, 47))
        self.label_password.setStyleSheet(u"font: 500 15pt \"\u7231\u5947\u827a\u9ed1\u4f53 Medium\";")
        self.label_username = QLabel(self.enroll_widget)
        self.label_username.setObjectName(u"label_username")
        self.label_username.setGeometry(QRect(158, 244, 127, 47))
        self.label_username.setStyleSheet(u"font: 500 15pt \"\u7231\u5947\u827a\u9ed1\u4f53 Medium\";")
        self.password_LineEdit = QLineEdit(self.enroll_widget)
        self.password_LineEdit.setObjectName(u"password_LineEdit")
        self.password_LineEdit.setGeometry(QRect(264, 348, 285, 45))
        self.password_LineEdit.setStyleSheet(u"font: 16pt \"\u65b9\u6b63\u7c97\u9ed1\u5b8b\u7b80\u4f53\";")
        self.username_LineEdit = QLineEdit(self.enroll_widget)
        self.username_LineEdit.setObjectName(u"username_LineEdit")
        self.username_LineEdit.setGeometry(QRect(264, 244, 285, 45))
        self.username_LineEdit.setStyleSheet(u"font: 16pt \"\u65b9\u6b63\u7c97\u9ed1\u5b8b\u7b80\u4f53\";")
        self.comfirm_LineEdit = QLineEdit(self.enroll_widget)
        self.comfirm_LineEdit.setObjectName(u"comfirm_LineEdit")
        self.comfirm_LineEdit.setGeometry(QRect(264, 450, 285, 45))
        self.comfirm_LineEdit.setStyleSheet(u"font: 16pt \"\u65b9\u6b63\u7c97\u9ed1\u5b8b\u7b80\u4f53\";")
        self.label_comfirm = QLabel(self.enroll_widget)
        self.label_comfirm.setObjectName(u"label_comfirm")
        self.label_comfirm.setGeometry(QRect(162, 450, 111, 47))
        self.label_comfirm.setStyleSheet(u"font: 500 15pt \"\u7231\u5947\u827a\u9ed1\u4f53 Medium\";")
        self.label_3.raise_()
        self.enrollButton.raise_()
        self.username_LineEdit.raise_()
        self.password_LineEdit.raise_()
        self.label_username.raise_()
        self.label_password.raise_()
        self.comfirm_LineEdit.raise_()
        self.label_comfirm.raise_()
        self.Button_last = QPushButton(self.centralwidget)
        self.Button_last.setObjectName(u"Button_last")
        self.Button_last.setGeometry(QRect(494, 2, 49, 41))
        self.Button_last.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	border-radius: 8px;\n"
"	background-color: transparent;\n"
"     padding: 10px;\n"
"     border-radius: 5px;\n"
"}\n"
"QPushButton:hover {\n"
"     background-color: rgba(244, 239, 231,220);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: transparent;\n"
"}")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditUndo))
        self.Button_last.setIcon(icon2)
        self.Button_last.setIconSize(QSize(22, 22))
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(550, 762, 83, 38))
        self.label_5.setStyleSheet(u"font: 900 15pt \"\u7231\u5947\u827a\u9ed1\u4f53 Black\";\n"
"")
        gui.setCentralWidget(self.centralwidget)
        self.background.raise_()
        self.closeButton.raise_()
        self.minimizeButton.raise_()
        self.time_label.raise_()
        self.Button_last.raise_()
        self.login_widget.raise_()
        self.enroll_widget.raise_()
        self.menu_widget.raise_()
        self.operator_widget.raise_()
        self.label_5.raise_()

        self.retranslateUi(gui)

        QMetaObject.connectSlotsByName(gui)
    # setupUi

    def retranslateUi(self, gui):
        gui.setWindowTitle(QCoreApplication.translate("gui", u"gui", None))
        self.background.setText("")
        self.loginButton.setText(QCoreApplication.translate("gui", u"\u767b\u5f55", None))
        self.label_2.setText("")
        self.label_Username.setText(QCoreApplication.translate("gui", u"UserName\uff1a", None))
        self.label_Password.setText(QCoreApplication.translate("gui", u"PassWord\uff1a", None))
        self.label_4.setText("")
#if QT_CONFIG(tooltip)
        self.btn_open_image.setToolTip(QCoreApplication.translate("gui", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_open_image.setText(QCoreApplication.translate("gui", u"\u6253\u5f00\u56fe\u7247", None))
        self.image_board.setText("")
#if QT_CONFIG(tooltip)
        self.btn_capture_frame.setToolTip(QCoreApplication.translate("gui", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_capture_frame.setText(QCoreApplication.translate("gui", u"\u5b9e\u65f6\u62cd\u6444", None))
        self.canema_save.setText("")
        self.text_meterocr_photo.setHtml(QCoreApplication.translate("gui", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'SimSun';\"><br /></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.btn_meter_ocr_photo.setToolTip(QCoreApplication.translate("gui", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_meter_ocr_photo.setText(QCoreApplication.translate("gui", u"\u8bc6\u522b\u7ed3\u679c", None))
        self.text_meterocr_camera.setHtml(QCoreApplication.translate("gui", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'SimSun';\"><br /></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.btn_meter_ocr_camera.setToolTip(QCoreApplication.translate("gui", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.btn_meter_ocr_camera.setText(QCoreApplication.translate("gui", u"\u8bc6\u522b\u7ed3\u679c", None))
        self.closeButton.setText("")
#if QT_CONFIG(shortcut)
        self.closeButton.setShortcut(QCoreApplication.translate("gui", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.minimizeButton.setText("")
#if QT_CONFIG(shortcut)
        self.minimizeButton.setShortcut(QCoreApplication.translate("gui", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.time_label.setText("")
        self.enroll_pushButton.setText(QCoreApplication.translate("gui", u"\u6ce8\u518c", None))
        self.login_pushButton.setText(QCoreApplication.translate("gui", u"\u767b\u5f55", None))
        self.label.setText("")
        self.enrollButton.setText(QCoreApplication.translate("gui", u"\u6ce8\u518c", None))
        self.label_3.setText("")
        self.label_password.setText(QCoreApplication.translate("gui", u"PassWord \uff1a", None))
        self.label_username.setText(QCoreApplication.translate("gui", u"UserName\uff1a", None))
        self.label_comfirm.setText(QCoreApplication.translate("gui", u"Comfirm  \uff1a", None))
        self.Button_last.setText("")
#if QT_CONFIG(shortcut)
        self.Button_last.setShortcut(QCoreApplication.translate("gui", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.label_5.setText(QCoreApplication.translate("gui", u"V 2.6.1.0", None))
    # retranslateUi

