# # gui.py
# class ExampleApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('OCR GUI')
#         self.setGeometry(300, 300, 600, 400)
#
#         # 添加标签用于显示图片
#         self.label_image = QLabel(self)
#         self.label_image.setGeometry(10, 10, 580, 280)
#         self.label_image.setAlignment(Qt.AlignCenter)
#         self.label_image.setText("No image selected")
#
#         # 添加文本框用于显示识别内容
#         self.textbox = QTextEdit(self)
#         self.textbox.setGeometry(10, 340, 580, 50)
#
#         # 添加按钮用于打开图片文件
#         self.btn_open = QPushButton('Open Image', self)
#         self.btn_open.setGeometry(10, 300, 100, 30)
#         self.btn_open.clicked.connect(self.open_image)
#
#         # 添加按钮用于执行 OCR
#         self.btn_ocr = QPushButton('Paddle OCR', self)
#         self.btn_ocr.setGeometry(120, 300, 100, 30)
#         self.btn_ocr.clicked.connect(self.Paddle_OCR)
#
#         # 添加按钮用于退出应用程序
#         self.btn_exit = QPushButton('Exit', self)
#         self.btn_exit.setGeometry(230, 300, 100, 30)
#         self.btn_exit.clicked.connect(self.close)
#
#     def open_image(self):
#         # 打开文件对话框，选择图片文件
#         file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image files (*.png *.jpg *.bmp)')
#         if file_path:
#             # 显示所选图片
#             pixmap = QPixmap(file_path)
#             pixmap = pixmap.scaledToWidth(580)  # 调整图片大小以适应标签
#             self.label_image.setPixmap(pixmap)
#             self.label_image.setAlignment(Qt.AlignCenter)
#             self.label_image.setText("")
#
#             self.image_path = file_path
#
#
#     def Paddle_OCR(self):
#         try:
#             # 执行 OCR
#             if hasattr(self, 'image_path'):
#                 image = cv2.imread(self.image_path)
#                 meterocr.meterocr(image)
#                 #gui.start_gui()
#                 #meterocr.PaddleOCR()
#             else:
#                 QMessageBox.warning(self, 'Warning', 'No image selected.')
#         except Exception as e:
#             QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
#
#
# def start_gui():
#     app = QApplication([])
#
#     ex = ExampleApp()
#     ex.show()
#     app.exec_()

# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton
# from PyQt5.QtCore import Qt, QTimer
# from PyQt5.QtGui import QPixmap
# import sys
# import cv2
# import datetime
# from PIL import Image
# from PyQt5.QtGui import QImage, QPixmap
# from threading import Thread
#
# class OCR_GUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle('OCR GUI')
#         self.setGeometry(300, 300, 600, 600)
#
#         # 添加标签用于显示时间
#         self.label_time = QLabel(self)
#         self.label_time.setGeometry(10, 10, 200, 30)
#         self.label_time.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         self.label_time.setStyleSheet("font-size: 14px; color: #333333;")
#
#         # 添加欢迎语
#         self.label_welcome = QLabel("欢迎使用meterocr！", self)
#         self.label_welcome.setGeometry(220, 10, 370, 30)
#         self.label_welcome.setAlignment(Qt.AlignCenter)
#         self.label_welcome.setStyleSheet("font-size: 16px; color: #007bff;")
#
#         # 添加标签用于显示图片
#         self.label_image = QLabel(self)
#         self.label_image.setGeometry(10, 50, 580, 280)
#         self.label_image.setAlignment(Qt.AlignCenter)
#         self.label_image.setText("No image selected")
#         self.label_image.setStyleSheet("background-color: #f0f0f0; border: 2px solid #cccccc;")
#
#         # 添加文本框用于显示识别内容
#         self.text_edit = QTextEdit(self)
#         self.text_edit.setGeometry(10, 340, 580, 260)
#         self.text_edit.setStyleSheet("background-color: #ffffff; border: 2px solid #cccccc;")
#
#         # 添加按钮用于打开图片文件
#         self.btn_open = QPushButton('打开图片', self)
#         self.btn_open.setGeometry(10, 300, 120, 30)
#         self.btn_open.setStyleSheet("background-color: #4CAF50; color: #ffffff; border: none;")
#         self.btn_open.clicked.connect(self.open_image)
#
#         # 添加按钮用于执行 OCR
#         self.btn_ocr = QPushButton('Paddle OCR', self)
#         self.btn_ocr.setGeometry(140, 300, 120, 30)
#         self.btn_ocr.setStyleSheet("background-color: #007bff; color: #ffffff; border: none;")
#         self.btn_ocr.clicked.connect(self.Paddle_OCR)
#
#         # 添加按钮用于拍照
#         self.btn_capture = QPushButton('拍照', self)
#         self.btn_capture.setGeometry(270, 300, 120, 30)
#         self.btn_capture.setStyleSheet("background-color: #ffc107; color: #ffffff; border: none;")
#         self.btn_capture.clicked.connect(self.capture_photo)
#
#         # 添加按钮用于退出应用程序
#         self.btn_exit = QPushButton('退出', self)
#         self.btn_exit.setGeometry(400, 300, 120, 30)
#         self.btn_exit.setStyleSheet("background-color: #dc3545; color: #ffffff; border: none;")
#         self.btn_exit.clicked.connect(self.close)
#
#         # 定时器用于更新时间显示
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_time)
#         self.timer.start(1000)
#
#     def update_time(self):
#         current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.label_time.setText(current_time)
#
#     def open_image(self):
#         # 在这里实现打开图片的逻辑
#         pass
#
#     def Paddle_OCR(self):
#         # 在这里实现执行OCR的逻辑
#         pass
#
#     def capture_photo(self):
#         # 在这里实现拍照的逻辑
#         thread = Thread(target=self.take_photo)
#         thread.start()
#
#     def take_photo(self):
#         camera = cv2.VideoCapture(0)
#         return_value, image = camera.read()
#         camera.release()
#
#         # 将OpenCV的图像转换为Qt可显示的格式
#         if return_value:
#             image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#             height, width, channel = image.shape
#             bytes_per_line = 3 * width
#             q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
#             pixmap = QPixmap.fromImage(q_image)
#             pixmap = pixmap.scaled(580, 280, Qt.KeepAspectRatio)
#             self.label_image.setPixmap(pixmap)
#             self.label_image.setAlignment(Qt.AlignCenter)
#             self.label_image.setText("")
#         else:
#             print("Failed to capture image")
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ocr_gui = OCR_GUI()
#     ocr_gui.show()
#     sys.exit(app.exec_())

import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QFileDialog


class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 创建标签以显示视频
        self.label_image = QLabel(self)
        self.label_image.setAlignment(Qt.AlignCenter)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.label_image)
        self.setLayout(layout)

        # 初始化摄像头
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("Error: Could not open camera.")
            return

        # 创建计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 每30毫秒更新一次帧

    def update_frame(self):
        return_value, image = self.camera.read()
        if return_value:
            # 转换颜色格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 获取图像尺寸
            height, width, channel = image.shape
            bytes_per_line = 3 * width

            # 创建QImage
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # 调整图像大小以适应标签
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaledToWidth(self.label_image.width())

            # 显示图像
            self.label_image.setPixmap(pixmap)
        else:
            print("Failed to capture image")

    def open_image(self):
        # 打开文件对话框，选择图片文件
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image files (*.png *.jpg *.bmp)')
        if file_path:
            # 显示所选图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaledToWidth(self.label_image.width())
            self.label_image.setPixmap(pixmap)
            self.label_image.setAlignment(Qt.AlignCenter)
            self.label_image.setText("")


# 主程序
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = CameraWidget()
    window.show()
    sys.exit(app.exec_())
