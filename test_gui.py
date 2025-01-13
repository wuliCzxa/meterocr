# test.py

# import os
# import sys
# import threading
# import time
# from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtWidgets import QFileDialog, QMessageBox
# import cv2
# import meterocr
#
#
# class CSGO(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.setObjectName("Form")
#         self.resize(1000, 800)
#         self.setStyleSheet("#Form{background-color: #303030; border-radius: 15px;}")
#
#         self.label_title_bar_top = QtWidgets.QLabel(self)
#         self.label_title_bar_top.setGeometry(QtCore.QRect(30, 30, 181, 31))
#         font = QtGui.QFont()
#         font.setFamily("微软雅黑")
#         font.setPointSize(-1)
#         font.setBold(True)
#         font.setWeight(75)
#         self.label_title_bar_top.setFont(font)
#         self.label_title_bar_top.setStyleSheet("color:Gray;\n"
#                                                 "border-radius: 7px;\n"
#                                                 "font-size:12px;")
#         self.label_title_bar_top.setObjectName("label_title_bar_top")
#         self.pushButton_2 = QtWidgets.QPushButton(self)
#         self.pushButton_2.setGeometry(QtCore.QRect(600, 50, 16, 16))
#         self.pushButton_2.setStyleSheet("QPushButton{\n"
#                                          "    background:#CE0000;\n"
#                                          "    color:white;\n"
#                                          "    box-shadow: 1px 1px 3px rgba(0,0,0,0.3);font-size:16px;border-radius: 8px;font-family: 微软雅黑;\n"
#                                          "}\n"
#                                          "QPushButton:hover{\n"
#                                          "    background:#FF2D2D;\n"
#                                          "}\n"
#                                          "QPushButton:pressed{\n"
#                                          "    border: 1px solid #3C3C3C!important;\n"
#                                          "}")
#         self.pushButton_2.setText("")
#         self.pushButton_2.setObjectName("pushButton_2")
#         self.pushButton_3 = QtWidgets.QPushButton(self)
#         self.pushButton_3.setGeometry(QtCore.QRect(570, 50, 16, 16))
#         self.pushButton_3.setStyleSheet("QPushButton{\n"
#                                          "    background:#6C6C6C;\n"
#                                          "    color:white;\n"
#                                          "    box-shadow: 1px 1px 3px rgba(0,0,0,0.3);font-size:16px;border-radius: 8px;font-family: 微软雅黑;\n"
#                                          "}\n"
#                                          "QPushButton:hover{\n"
#                                          "    background:#9D9D9D;\n"
#                                          "}\n"
#                                          "QPushButton:pressed{\n"
#                                          "    border: 1px solid #3C3C3C!important;\n"
#                                          "}")
#         self.pushButton_3.setText("")
#         self.pushButton_3.setObjectName("pushButton_3")
#
#         self.tabWidget = QtWidgets.QTabWidget(self)
#         self.tabWidget.setGeometry(QtCore.QRect(30, 80, 941, 691))
#         self.tabWidget.setStyleSheet("#tabWidget::pane {border: none;}")
#         self.tabWidget.setObjectName("tabWidget")
#         self.tabWidget.currentChanged.connect(self.tab_changed)
#
#         self.tab = QtWidgets.QWidget()
#         self.tab.setObjectName("tab")
#         self.tabWidget.addTab(self.tab, "Function")
#
#         self.pushButton_camera = QtWidgets.QPushButton(self.tab)
#         self.pushButton_camera.setGeometry(QtCore.QRect(50, 50, 211, 61))
#         self.pushButton_camera.setText("Open Camera")
#         self.pushButton_camera.clicked.connect(self.open_camera)
#
#         self.pushButton_take_photo = QtWidgets.QPushButton(self.tab)
#         self.pushButton_take_photo.setGeometry(QtCore.QRect(50, 150, 211, 61))
#         self.pushButton_take_photo.setText("Take Photo")
#         self.pushButton_take_photo.clicked.connect(self.take_photo)
#
#         self.pushButton_open_image = QtWidgets.QPushButton(self.tab)
#         self.pushButton_open_image.setGeometry(QtCore.QRect(50, 250, 211, 61))
#         self.pushButton_open_image.setText("Open Image")
#         self.pushButton_open_image.clicked.connect(self.open_image)
#
#         self.label_image = QtWidgets.QLabel(self.tab)
#         self.label_image.setGeometry(QtCore.QRect(300, 50, 580, 540))
#         self.label_image.setAlignment(Qt.AlignCenter)
#         self.label_image.setStyleSheet("border: 2px solid gray; border-radius: 10px;")
#         self.label_image.setText("No Image")
#
#         self.tab_2 = QtWidgets.QWidget()
#         self.tab_2.setObjectName("tab_2")
#         self.tabWidget.addTab(self.tab_2, "Paddle OCR")
#
#         self.pushButton_paddle_ocr = QtWidgets.QPushButton(self.tab_2)
#         self.pushButton_paddle_ocr.setGeometry(QtCore.QRect(50, 50, 211, 61))
#         self.pushButton_paddle_ocr.setText("Paddle OCR")
#         self.pushButton_paddle_ocr.clicked.connect(self.paddle_ocr)
#
#         self.text_edit = QtWidgets.QTextEdit(self.tab_2)
#         self.text_edit.setGeometry(QtCore.QRect(300, 50, 580, 540))
#         self.text_edit.setStyleSheet("border: 2px solid gray; border-radius: 10px;")
#
#         self.tab_21 = QtWidgets.QWidget()
#         self.tab_21.setObjectName("tab_21")
#         self.tabWidget.addTab(self.tab_21, "About")
#
#         self.label_title_bar_top_3 = QtWidgets.QLabel(self.tab_21)
#         self.label_title_bar_top_3.setGeometry(QtCore.QRect(20, 30, 181, 31))
#         font = QtGui.QFont()
#         font.setFamily("微软雅黑")
#         font.setPointSize(-1)
#         font.setBold(True)
#         font.setWeight(75)
#         self.label_title_bar_top_3.setFont(font)
#         self.label_title_bar_top_3.setStyleSheet("color:Gray;\n"
#                                                   "border-radius: 7px;\n"
#                                                   "font-size:12px;")
#         self.label_title_bar_top_3.setObjectName("label_title_bar_top_3")
#
#         self.retranslateUi(self)
#         self.tabWidget.setCurrentIndex(0)
#         QtCore.QMetaObject.connectSlotsByName(self)
#
#     def retranslateUi(self, Form):
#         _translate = QtCore.QCoreApplication.translate
#         Form.setWindowTitle(_translate("Form", "Form"))
#         self.label_title_bar_top.setText(_translate("Form", "    Breath Team"))
#         self.label_title_bar_top_3.setText(_translate("Form", "About"))
#
#     def tab_changed(self, index):
#         if index == 0:
#             pass
#         elif index == 1:
#             pass
#         elif index == 2:
#             pass
#
#     def open_camera(self):
#         # Your code for opening the camera goes here
#         pass
#
#     def take_photo(self):
#         # Your code for taking a photo goes here
#         pass
#
#     def open_image(self):
#         # Your code for opening an image goes here
#         pass
#
#     def paddle_ocr(self):
#         # Your code for performing OCR using PaddleOCR goes here
#         pass
#
#
# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     gui = CSGO()
#     gui.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize

import cv2
import numpy as np
import paddlehub as hub

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("功能演示")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.tabs.addTab(self.tab1, "Function")
        self.tabs.addTab(self.tab2, "Paddle")
        self.tabs.addTab(self.tab3, "About")

        self.init_tab1()
        self.init_tab2()
        self.init_tab3()

    def init_tab1(self):
        layout = QVBoxLayout()

        self.camera_label = QLabel()
        self.camera_label.setFixedSize(640, 480)
        layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        self.capture_button = QPushButton("Capture Image")
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setFixedSize(200, 50)
        layout.addWidget(self.capture_button, alignment=Qt.AlignCenter)

        self.tab1.setLayout(layout)

    def init_tab2(self):
        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        self.ocr_button = QPushButton("Run OCR")
        self.ocr_button.clicked.connect(self.run_ocr)
        self.ocr_button.setFixedSize(200, 50)
        layout.addWidget(self.ocr_button, alignment=Qt.AlignCenter)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFixedSize(400, 200)
        layout.addWidget(self.result_text, alignment=Qt.AlignCenter)

        self.tab2.setLayout(layout)

    def init_tab3(self):
        layout = QVBoxLayout()
        label = QLabel("This tab is empty for now.")
        font = QFont("Arial", 12)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.tab3.setLayout(layout)

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            image = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaledToWidth(640) # Scale pixmap to fit label width
            self.camera_label.setPixmap(pixmap)
            self.camera_label.setScaledContents(True)

            # Add animation
            self.animate_button(self.camera_label)

    def run_ocr(self):
        image = cv2.imread("captured_image.jpg")
        ocr = hub.Module(name="chinese_ocr_db_crnn_mobile")
        result = ocr.recognize_text(images=[image])
        self.result_text.setPlainText(result[0]["data"])

    def animate_button(self, widget):
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        original_geometry = widget.geometry()
        animation.setKeyValueAt(0, original_geometry)
        animation.setKeyValueAt(0.1, original_geometry.adjusted(-5, -5, 5, 5))
        animation.setKeyValueAt(0.5, original_geometry)
        animation.setKeyValueAt(0.9, original_geometry.adjusted(-5, -5, 5, 5))
        animation.setEndValue(original_geometry)
        animation.start(QPropertyAnimation.DeleteWhenStopped)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the stylesheet
    with open("styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
