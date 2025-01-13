from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, \
    QMessageBox, QTextEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
from meterocr import meterocr
import threading

from func_ocr import *


import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("摄像头应用")
        self.root.geometry("640x480")

        # 摄像头调用
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("无法打开摄像头")
            exit()

        # 显示摄像头画面的区域
        self.camera_label = tk.Label(self.root)
        self.camera_label.pack(pady=10)

        # 拍照按钮
        self.capture_btn = ttk.Button(self.root, text="拍照", command=self.capture_photo)
        self.capture_btn.pack(pady=5)

        # 退出按钮
        self.quit_btn = ttk.Button(self.root, text="退出", command=self.quit_app)
        self.quit_btn.pack(pady=5)

        self.show_camera()

    def show_camera(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_label.config(image=self.photo)
        self.camera_label.after(10, self.show_camera)  # 每10毫秒更新画面

    def capture_photo(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite("snapshot.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            print("照片已保存为snapshot.jpg")

    def quit_app(self):
        self.cap.release()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()


class ExampleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OCR GUI')
        self.setGeometry(300, 300, 600, 760)

        # 添加标签用于显示图片
        self.label_image = QLabel(self)
        self.label_image.setGeometry(10, 10, 580, 280)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.setText("No image selected")

        # 添加文本框用于显示识别内容
        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 390, 580, 370)  # 设置文本框的位置和大小

        # self.display_text()

        # 添加按钮用于打开图片文件
        self.btn_open = QPushButton('Open Image', self)
        self.btn_open.setGeometry(10, 350, 100, 30)
        self.btn_open.clicked.connect(self.open_image)

        # 添加按钮用于执行 OCR()
        self.btn_ocr = QPushButton('Paddle OCR', self)
        self.btn_ocr.setGeometry(120, 350, 100, 30)
        self.btn_ocr.clicked.connect(self.Paddle_OCR)

        # 创建一个按钮
        self.open_button = QPushButton("Open File", self)
        self.open_button.setGeometry(230, 350, 100, 30)  # 设置按钮的位置和大小
        # self.open_button.clicked.connect(self.display_text)

        # 添加按钮用于退出应用程序
        self.btn_exit = QPushButton('Exit', self)
        self.btn_exit.setGeometry(340, 350, 100, 30)
        self.btn_exit.clicked.connect(self.close)

    def open_image(self):
        # 打开文件对话框，选择图片文件
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image files (*.png *.jpg *.bmp)')
        if file_path:
            # 显示所选图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaledToWidth(580)  # 调整图片大小以适应标签
            self.label_image.setPixmap(pixmap)
            self.label_image.setAlignment(Qt.AlignCenter)
            self.label_image.setText("")

            self.image_path = file_path

    def display_text(self):
        file_path = "D:\\newmeterocr\\meterocr\\result.txt"  # 指定文件路径
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("文件不存在或无法打开。")
            return

        # 显示文件内容
        self.text_edit.setPlainText(text)


    def Paddle_OCR(self):
        try:
            # 执行 OCR
            if hasattr(self, 'image_path'):
                image = cv2.imread(self.image_path)
                meterocr.meterocr(image)
                # height, width = image.shape[:2]
                # rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
                # rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
                # meterocr.meterocr(rotated_image)

                self.display_text()
                # 将识别出的文字信息显示在文本框中
                # self.display_text()
                #gui.start_gui()
                #meterocr.PaddleOCR()
            else:
                QMessageBox.warning(self, 'Warning', 'No image selected.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')



def start_gui():
    app = QApplication([])

    ex = ExampleApp()
    ex.show()
    app.exec_()






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
        file_path = "E:\\Software\\JetBrains\\Python Project\\newmeterocr_001\\meterocr\\result.txt"  # 指定文件路径
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
        file_path = "E:\\Software\\JetBrains\\Python Project\\newmeterocr_001\\meterocr\\log.txt"  # 指定文件路径
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("文件不存在或无法打开。")
            return

        # 显示文件内容
        self.text_data_ocr.setPlainText(text)

    def open_camera(self):
        self.camera = cv2.VideoCapture(0)  # 0代表默认摄像头，1代表外接摄像头

        if not self.camera.isOpened():
            QMessageBox.warning(self, 'Warning', 'Failed to open camera.')
        else:
            self.timer_camera.start(20)  # 20毫秒更新一次画面

    # def take_photo(self, file_path):
    #     pixmap = QPixmap(file_path)
    #     self.label_21.setPixmap(pixmap.scaled(self.label_21.size(), Qt.KeepAspectRatio))
    #     self.label_21.setAlignment(Qt.AlignCenter)

    def take_photo(self):
        if self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Generate a file name for the captured image
                timestamp = QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')
                file_path = f"captured_{timestamp}.bmp"

                # Save the frame as an image file
                cv2.imwrite(file_path, frame)

                # Display the captured image
                pixmap = QPixmap(file_path)
                self.label_21.setPixmap(pixmap.scaled(self.label_20.size(), Qt.KeepAspectRatio))
                self.label_21.setAlignment(Qt.AlignCenter)

                self.image_path_test = file_path
        else:
            QMessageBox.warning(self, 'Warning', 'Camera is not opened.')


    def update_frame(self):
        if self.camera is not None and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.label_20.setPixmap(pixmap.scaled(self.label_20.size(), Qt.KeepAspectRatio))
                self.label_20.setAlignment(Qt.AlignCenter)

    def Paddle_OCR(self):
        try:
            # 执行 OCR
            image_path = getattr(self, 'image_path', None)
            image_path_test = getattr(self, 'image_path_test', None)

            print("image_path:", image_path)
            print("image_path_test:", image_path_test)

            if image_path:
                image = cv2.imread(image_path)
                meterocr.meterocr(image)

            elif image_path_test:
                image = cv2.imread(image_path_test)
                meterocr.meterocr(image)
            else:
                QMessageBox.warning(self, 'Warning', 'No image selected.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

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


# import sys
# import cv2
# from PyQt5.QtCore import Qt, QTimer, QDateTime, QTime, QThread, pyqtSignal
# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.uic import loadUi
# from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
# import meterocr
#
# class OCRThread(QThread):
#     finished = pyqtSignal()
#     def __init__(self, image_path, parent=None):
#         super(OCRThread, self).__init__(parent)
#         self.image_path = image_path
#
#     def run(self):
#         image = cv2.imread(self.image_path)
#         meterocr.meterocr(image)
#         self.finished.emit()
#
# class MyMainWindow(QMainWindow):
#     def __init__(self):
#         super(MyMainWindow, self).__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint)
#         loadUi("untitled.ui", self)
#
#         self.btn_close.clicked.connect(self.close)
#         self.btn_minimize.clicked.connect(self.showMinimized)
#         self.btn_open_camera.clicked.connect(self.open_camera)
#         self.btn_capture_frame.clicked.connect(self.take_photo)
#         self.btn_open_image.clicked.connect(self.open_image)
#         self.btn_meter_ocr.clicked.connect(self.start_ocr_thread)
#         self.btn_screen_information.clicked.connect(self.display_text)
#         self.btn_historical_data.clicked.connect(self.display_data_text)
#
#         self.camera = None
#         self.timer_camera = QTimer()
#         self.timer_camera.timeout.connect(self.update_frame)
#
#         self.timer_clock = QTimer()
#         self.timer_clock.timeout.connect(self.update_time)
#         self.timer_clock.start(1000)
#
#     def open_image(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, 'open image', '', 'Image files (*.png *.jpg *.bmp)')
#         if file_path:
#             pixmap = QPixmap(file_path)
#             pixmap = pixmap.scaledToWidth(471)
#             self.image.setPixmap(pixmap)
#             self.image.setAlignment(Qt.AlignCenter)
#             self.image.setText("")
#             self.image_path = file_path
#
#     def display_text(self):
#         file_path = "result.txt"
#         try:
#             with open(file_path, 'r') as file:
#                 text = file.read()
#             self.text_meterocr.setPlainText(text)
#         except FileNotFoundError:
#             print("File not found or cannot be opened.")
#
#     def display_data_text(self):
#         file_path = "log.txt"
#         try:
#             with open(file_path, 'r') as file:
#                 text = file.read()
#             self.text_data_ocr.setPlainText(text)
#         except FileNotFoundError:
#             print("File not found or cannot be opened.")
#
#     def open_camera(self):
#         self.camera = cv2.VideoCapture(0)
#         if not self.camera.isOpened():
#             QMessageBox.warning(self, 'Warning', 'Failed to open camera.')
#         else:
#             self.timer_camera.start(20)
#
#     def take_photo(self):
#         if self.camera and self.camera.isOpened():
#             ret, frame = self.camera.read()
#             if ret:
#                 timestamp = QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')
#                 file_path = f"captured_{timestamp}.bmp"
#                 cv2.imwrite(file_path, frame)
#                 pixmap = QPixmap(file_path)
#                 self.label_21.setPixmap(pixmap.scaled(self.label_20.size(), Qt.KeepAspectRatio))
#                 self.label_21.setAlignment(Qt.AlignCenter)
#                 self.image_path_test = file_path
#         else:
#             QMessageBox.warning(self, 'Warning', 'Camera is not opened.')
#
#     def update_frame(self):
#         if self.camera and self.camera.isOpened():
#             ret, frame = self.camera.read()
#             if ret:
#                 rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 h, w, ch = rgb_image.shape
#                 bytes_per_line = ch * w
#                 q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
#                 pixmap = QPixmap.fromImage(q_img)
#                 self.label_20.setPixmap(pixmap.scaled(self.label_20.size(), Qt.KeepAspectRatio))
#                 self.label_20.setAlignment(Qt.AlignCenter)
#
#     def start_ocr_thread(self):
#         image_path = getattr(self, 'image_path', None)
#         image_path_test = getattr(self, 'image_path_test', None)
#         selected_image_path = image_path if image_path else image_path_test
#         if selected_image_path:
#             self.ocr_thread = OCRThread(selected_image_path)
#             self.ocr_thread.finished.connect(self.ocr_thread_finished)
#             self.ocr_thread.start()
#         else:
#             QMessageBox.warning(self, 'Warning', 'No image selected.')
#
#     def ocr_thread_finished(self):
#         QMessageBox.information(self, 'Info', 'OCR processing finished.')
#
#     def update_time(self):
#         current_time = QTime.currentTime()
#         display_text = current_time.toString('hh:mm:ss')
#         self.label_time.setText(display_text)
#
#     def closeEvent(self, event):
#         if self.camera and self.camera.isOpened():
#             self.camera.release()
#         event.accept()
#
# def start_gui():
#     app = QApplication(sys.argv)
#     main_window = MyMainWindow()
#     main_window.show()
#     sys.exit(app.exec_())






# if __name__ == "__main__":
#     start_gui()

