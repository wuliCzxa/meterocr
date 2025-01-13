from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, \
    QMessageBox, QTextEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
import meterocr
import threading

from func_ocr import *


# import cv2
# import tkinter as tk
# from tkinter import ttk
# from PIL import Image, ImageTk

# class CameraApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("摄像头应用")
#         self.root.geometry("640x480")
#
#         # 摄像头调用
#         self.cap = cv2.VideoCapture(0)
#         if not self.cap.isOpened():
#             print("无法打开摄像头")
#             exit()
#
#         # 显示摄像头画面的区域
#         self.camera_label = tk.Label(self.root)
#         self.camera_label.pack(pady=10)
#
#         # 拍照按钮
#         self.capture_btn = ttk.Button(self.root, text="拍照", command=self.capture_photo)
#         self.capture_btn.pack(pady=5)
#
#         # 退出按钮
#         self.quit_btn = ttk.Button(self.root, text="退出", command=self.quit_app)
#         self.quit_btn.pack(pady=5)
#
#         self.show_camera()
#
#     def show_camera(self):
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
#             self.camera_label.config(image=self.photo)
#         self.camera_label.after(10, self.show_camera)  # 每10毫秒更新画面
#
#     def capture_photo(self):
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             cv2.imwrite("snapshot.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
#             print("照片已保存为snapshot.jpg")
#
#     def quit_app(self):
#         self.cap.release()
#         self.root.quit()
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = CameraApp(root)
#     root.mainloop()


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
                height, width = image.shape[:2]
                rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
                rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
                meterocr.meterocr(rotated_image)

                self.display_text()
                # 将识别出的文字信息显示在文本框中
                # self.display_text()
                #gui.start_gui()
                #meterocr.PaddleOCR()
            else:
                QMessageBox.warning(self, 'Warning', 'No image selected.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')



def start_GUI():
    app = QApplication([])

    ex = ExampleApp()
    ex.show()
    app.exec_()


