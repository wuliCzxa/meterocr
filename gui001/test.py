# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from PyQt5.uic import loadUi
# import threading, time, os, sys
# from PyQt5.QtCore import QUrl
# from PyQt5.Qt import *
# from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
# from PyQt5 import QtCore, QtGui, QtWidgets
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint)
#         loadUi("untitled.ui", self)
#         self.btn_close.clicked.connect(self.close)
#         self.btn_minimize.clicked.connect(self.showMinimized)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

# import sys
# import cv2
# from PyQt5.QtCore import Qt, QTimer, QDateTime
# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from PyQt5.uic import loadUi
# import pytesseract
# from PIL import ImageGrab
#
# class MyMainWindow(QMainWindow):
#     def __init__(self):
#         super(MyMainWindow, self).__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint)
#         loadUi("untitled.ui", self)
#         self.timer_camera = QTimer()  # 定义定时器，用于捕获摄像头画面
#         self.timer_camera.timeout.connect(self.show_camera)  # 绑定定时器到show_camera函数
#
#         self.btn_close.clicked.connect(self.close)
#         self.btn_minimize.clicked.connect(self.showMinimized)
#         self.btn_close_3.clicked.connect(self.run_meter_ocr)
#         self.btn_close_4.clicked.connect(self.capture_screen)
#
#         self.start_camera()
#
#         # 设置定时器，每秒更新一次时间
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_time)
#         self.timer.start(1000)
#
#     def start_camera(self):
#         self.capture = cv2.VideoCapture(0)  # 打开摄像头
#         self.timer_camera.start(30)  # 设置定时器超时时间
#
#     def show_camera(self):
#         ret, frame = self.capture.read()  # 读取摄像头画面
#         if ret:
#             image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换为RGB格式
#             height, width, channels = image.shape
#             bytesPerLine = channels * width
#             convertToQtFormat = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
#             p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
#             self.label.setPixmap(QPixmap.fromImage(p))  # 在label上显示摄像头画面
#
#     def run_meter_ocr(self):
#         ret, frame = self.capture.read()  # 读取摄像头画面
#         if ret:
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             text = pytesseract.image_to_string(gray)
#             self.meterocr.setPlainText(text)
#
#     def capture_screen(self):
#         screen = ImageGrab.grab()  # 获取屏幕截图
#         text = pytesseract.image_to_string(screen)
#         self.meterocr_2.setPlainText(text)
#
#     def update_time(self):
#         current_time = QDateTime.currentDateTime()
#         display_text = current_time.toString("yyyy-MM-dd hh:mm:ss")
#         self.label_3.setText(display_text)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MyMainWindow()
#     main_window.show()
#     sys.exit(app.exec_())


import sys
import cv2
import pytesseract
from PIL import ImageGrab
from PyQt5.QtCore import Qt, QTimer, QDateTime, QTime
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, \
    QMessageBox, QTextEdit
from PyQt5.QtCore import Qt
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import meterocr
import threading

from func_ocr import *


class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        loadUi("untitled.ui", self)
        # self.timer_camera = QTimer()  # 定义定时器，用于捕获摄像头画面
        # self.timer_camera.timeout.connect(self.show_camera)  # 绑定定时器到show_camera函数

        self.btn_close.clicked.connect(self.close)
        self.btn_minimize.clicked.connect(self.showMinimized)
        #打开摄像头
        self.btn_open_camera.clicked.connect(self.open_camera)

        self.camera = None
        self.timer_camera = QTimer()
        self.timer_camera.timeout.connect(self.update_frame)

        self.timer_clock = QTimer()
        self.timer_clock.timeout.connect(self.update_time)
        self.timer_clock.start(1000)  # 更新时间间隔为1秒

        #拍照
        self.btn_capture_frame.clicked.connect(self.take_photo)
        #打开图片
        self.btn_open_image.clicked.connect(self.open_image)
        #进行识别
        self.btn_meter_ocr.clicked.connect(self.Paddle_OCR)
        #返回识别结果
        self.btn_screen_information.clicked.connect(self.display_text)
        #查看历史记录
        self.btn_historical_data.clicked.connect(self.display_data_text)

        # # 设置定时器，每秒更新一次时间
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_time)
        # self.timer.start(1000)

#     def __init__(self):
#         super(MainWindow, self).__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint)
#         loadUi("untitled.ui", self)
#         self.btn_close.clicked.connect(self.close)
#         self.btn_minimize.clicked.connect(self.showMinimized)

    def open_image(self):
        # 打开文件对话框，选择图片文件
        file_path, _ = QFileDialog.getOpenFileName(self, 'open image', '', 'Image files (*.png *.jpg *.bmp)')
        if file_path:
            # 显示所选图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaledToWidth(471)  # 调整图片大小以适应标签
            self.image.setPixmap(pixmap)
            self.image.setAlignment(Qt.AlignCenter)
            self.image.setText("")

            self.image_path = file_path

    def display_text(self):
        file_path = "E:\\Software\\JetBrains\\Python Project\\newmeterocr\\meterocr\\result.txt"  # 指定文件路径
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("文件不存在或无法打开。")
            return

        # 显示文件内容
        self.text_meterocr.setPlainText(text)

    def display_data_text(self):
        file_path = "E:\\Software\\JetBrains\\Python Project\\newmeterocr\\meterocr\\log.txt"  # 指定文件路径
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("文件不存在或无法打开。")
            return

        # 显示文件内容
        self.text_data_ocr.setPlainText(text)

    def Paddle_OCR(self):
        try:
            # 执行 OCR
            if hasattr(self, 'image_path'):
                image = cv2.imread(self.image_path)
                height, width = image.shape[:2]
                rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
                rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
                meterocr.meterocr(rotated_image)

                # self.display_text()

            else:
                QMessageBox.warning(self, 'Warning', 'No image selected.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    # def open_camera(self):
    #     self.camera = cv2.VideoCapture(0)  # 0代表默认摄像头，1代表外接摄像头
    #
    #     if not self.camera.isOpened():
    #         QMessageBox.warning(self, 'Warning', 'Failed to open camera.')
    #     else:
    #         self.timer_camera.start(50)  # 50毫秒更新一次画面
    #
    # def take_photo(self):
    #     if self.camera is not None and self.camera.isOpened():
    #         ret, frame = self.camera.read()
    #         if ret:
    #             file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image files (*.png *.jpg *.bmp)')
    #             if file_path:
    #                 cv2.imwrite(file_path, frame)
    #                 self.image_path = file_path
    #                 pixmap = QPixmap(file_path)
    #                 self.central_widget.setPixmap(pixmap.scaled(self.central_widget.size(), Qt.KeepAspectRatio))
    #                 self.central_widget.setAlignment(Qt.AlignCenter)
    #
    # def update_frame(self):
    #     if self.camera is not None and self.camera.isOpened():
    #         ret, frame = self.camera.read()
    #         if ret:
    #             rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #             h, w, ch = rgb_image.shape
    #             bytes_per_line = ch * w
    #             q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #             pixmap = QPixmap.fromImage(q_img)
    #             self.central_widget.setPixmap(pixmap.scaled(self.central_widget.size(), Qt.KeepAspectRatio))
    #             self.central_widget.setAlignment(Qt.AlignCenter)

    def open_camera(self):
        # self.camera = cv2.VideoCapture(0)  # 0代表默认摄像头，1代表外接摄像头
        #
        # if not self.camera.isOpened():
        #     QMessageBox.warning(self, 'Warning', 'Failed to open camera.')
        # else:
        #     self.timer_camera.start(50)  # 50毫秒更新一次画面
        cv2.namedWindow('video', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('video', 640, 480)

        # 如果打开失败, 不会报错.
        # cap = cv2.VideoCapture(1)
        self.camera = cv2.VideoCapture(0)

        # 循环读取摄像头的每一帧
        if not self.camera.isOpened():
            QMessageBox.warning(self, 'Warning', 'Failed to open camera.')
        else:
            # while True:
            while self.camera.isOpened():
                # 读一帧数据, 返回标记和这一帧数据. True表示读到了数据, False表示没读到数据.
                ret, frame = self.camera.read()
                # 可以根据ret做个判断
                if not ret:
                    # 没读到数据, 直接退出
                    break
                # 显示数据
                cv2.imshow('video', frame)
            # 别忘了释放资源
            self.camera.release()
            cv2.destroyAllWindows()

    def take_photo(self):
        if self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image files (*.png *.jpg *.bmp)')
                if file_path:
                    cv2.imwrite(file_path, frame)
                    self.image_path = file_path
                    pixmap = QPixmap(file_path)
                    self.central_widget.setPixmap(pixmap.scaled(self.central_widget.size(), Qt.KeepAspectRatio))
                    self.central_widget.setAlignment(Qt.AlignCenter)

    def update_frame(self):
        if self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.centralwidget.setPixmap(pixmap.scaled(self.central_widget.size(), Qt.KeepAspectRatio))
                self.centralwidget.setAlignment(Qt.AlignCenter)

    def update_time(self):
        current_time = QTime.currentTime()
        display_text = current_time.toString('hh:mm:ss')
        self.label_time.setText(display_text)

    def closeEvent(self, event):
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
        event.accept()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MyMainWindow()
#     main_window.show()
#     sys.exit(app.exec_())
def start_gui_test():
    app = QApplication(sys.argv)

    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())
