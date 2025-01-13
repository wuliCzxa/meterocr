import sys
import os
import cv2
import pytesseract
from PIL import Image
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QLineEdit, QTextEdit
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from datetime import datetime, timedelta
from ui_form import Ui_gui  # 确保正确生成的 ui_form 文件

import meterocr
import threading

from func_ocr import *

class OcrThread(QThread):
    ocr_finished = Signal(str)  # 用于传递OCR结果

    def __init__(self, image, is_camera=False):
        super().__init__()
        self.image = image
        self.is_camera = is_camera

    def run(self):
        # 使用meterocr进行识别（根据图片或摄像头帧处理）
        try:
            if self.is_camera:
                result = meterocr.meterocr(self.image)
            else:
                result = meterocr.meterocr(self.image)

            # 将识别结果通过信号传回主线程
            if result:
                self.ocr_finished.emit("\n".join(result))
            else:
                self.ocr_finished.emit("未识别出有效的文本。")
        except Exception as e:
            self.ocr_finished.emit(f"OCR 识别出错: {str(e)}")

class gui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_gui()
        self.ui.setupUi(self)

        # 移除窗口标题
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 初始化变量
        self.old_position = None
        self.users = {}
        self.current_image_path = None  # 当前选择的图片路径
        self.captured_frame = None  # 保存拍摄的帧
        self.camera = None  # 用于保存摄像头
        self.timer_camera = QTimer(self)  # 用于摄像头显示

        # 加载已保存的用户
        self.loadUsers()

        # 连接按钮与对应功能
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.minimizeButton.clicked.connect(self.showMinimized)
        self.ui.enroll_pushButton.clicked.connect(self.gotoEnroll)
        self.ui.enrollButton.clicked.connect(self.enrollUser)
        self.ui.loginButton.clicked.connect(self.loginUser)
        self.ui.login_pushButton.clicked.connect(self.gotoLogin)
        self.ui.Button_last.clicked.connect(self.showMenu)
        self.ui.btn_open_image.clicked.connect(self.openImage)  # 选择并显示图片
        self.ui.btn_meter_ocr_photo.clicked.connect(self.performOcrOnPhoto)  # 图片 OCR 识别
        self.ui.btn_capture_frame.clicked.connect(self.toggleCamera)  # 摄像头开关及拍照
        self.ui.btn_meter_ocr_camera.clicked.connect(self.performOcrOnCameraFrame)  # 摄像头拍照 OCR 识别

        # 密码输入框隐藏字符
        self.ui.password_LineEdit.setEchoMode(QLineEdit.Password)
        self.ui.comfirm_LineEdit.setEchoMode(QLineEdit.Password)
        self.ui.Password_LineEdit.setEchoMode(QLineEdit.Password)

        # 启动时钟
        self.startClock()

        # 初始化界面可见性
        self.initUIVisibility()

    def showMenu(self):
        # 显示菜单，隐藏其他窗口
        self.ui.menu_widget.setVisible(True)
        self.ui.closeButton.setVisible(True)
        self.ui.minimizeButton.setVisible(True)
        self.ui.background.setVisible(True)
        self.ui.time_label.setVisible(True)
        self.ui.enroll_widget.setVisible(False)
        self.ui.login_widget.setVisible(False)
        self.ui.operator_widget.setVisible(False)

    def initUIVisibility(self):
        # 初始化显示菜单界面，隐藏其他窗口
        self.ui.menu_widget.setVisible(True)
        self.ui.enroll_widget.setVisible(False)
        self.ui.login_widget.setVisible(False)
        self.ui.operator_widget.setVisible(False)
        self.ui.closeButton.setVisible(True)
        self.ui.minimizeButton.setVisible(True)
        self.ui.background.setVisible(True)
        self.ui.time_label.setVisible(True)

    def gotoEnroll(self):
        # 切换到注册界面
        self.ui.menu_widget.setVisible(False)
        self.ui.login_widget.setVisible(False)
        self.ui.operator_widget.setVisible(False)
        self.ui.enroll_widget.setVisible(True)

    def enrollUser(self):
        # 注册用户逻辑
        username = self.ui.username_LineEdit.text()
        password = self.ui.password_LineEdit.text()
        comfirm_password = self.ui.comfirm_LineEdit.text()

        if not username or not password or not comfirm_password:
            QMessageBox.warning(self, "错误", "用户名、密码和确认密码不能为空！")
            return

        if password != comfirm_password:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致！")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "错误", "密码长度必须不少于6位！")
            return

        if username in self.users:
            QMessageBox.warning(self, "错误", "用户名已存在！")
            return

        self.users[username] = password
        self.saveUsers()
        QMessageBox.information(self, "成功", "注册成功！")
        self.ui.enroll_widget.setVisible(False)
        self.ui.login_widget.setVisible(True)

    def loginUser(self):
        # 登录用户逻辑
        username = self.ui.Username_LineEdit.text()
        password = self.ui.Password_LineEdit.text()

        if username not in self.users:
            QMessageBox.warning(self, "错误", "该用户不存在！")
            return

        if self.users[username] == password:
            QMessageBox.information(self, "成功", "登录成功！")
            self.ui.menu_widget.setVisible(False)
            self.ui.operator_widget.setVisible(True)
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")

    def gotoLogin(self):
        # 切换到登录界面
        self.ui.menu_widget.setVisible(False)
        self.ui.enroll_widget.setVisible(False)
        self.ui.operator_widget.setVisible(False)
        self.ui.login_widget.setVisible(True)

    # def openImage(self):
    #     # 打开文件对话框，选择图片，并显示在 image_board
    #     image_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
    #     if image_path:
    #         self.current_image_path = image_path
    #         pixmap = QPixmap(image_path)
    #         self.ui.image_board.setPixmap(pixmap)
    #         self.ui.image_board.setScaledContents(True)

    def toggleCamera(self):
        # 打开/关闭摄像头，并捕获帧
        if self.camera is None:  # 摄像头未初始化时，打开摄像头
            self.camera = cv2.VideoCapture(0)
            self.timer_camera.timeout.connect(self.updateCameraFrame)
            self.timer_camera.start(30)  # 每 30 毫秒更新一次
        else:  # 摄像头已打开时，捕获帧
            self.captureFrame()

    def updateCameraFrame(self):
        # 更新摄像头画面并显示在 canema_save 标签中
        ret, frame = self.camera.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.ui.canema_save.setPixmap(QPixmap.fromImage(qt_image))
            self.ui.canema_save.setScaledContents(True)

    def captureFrame(self):
        # 捕获当前摄像头画面并停止摄像头
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.captured_frame = frame
                self.timer_camera.stop()
                self.camera.release()
                self.camera = None
                # 显示捕获的帧
                self.displayCapturedFrame(self.captured_frame)

    def displayCapturedFrame(self, frame):
        # 将捕获的帧显示在 canema_save 标签中
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.ui.canema_save.setPixmap(QPixmap.fromImage(qt_image))
        self.ui.canema_save.setScaledContents(True)

    # def performOcrOnPhoto(self):
    #     # 对显示在 image_board 中的图片进行 OCR 识别
    #     try:
    #         if self.current_image_path:
    #             # 读取当前选择的图片
    #             image = cv2.imread(self.current_image_path)
    #
    #             # 检查图片是否成功读取
    #             if image is not None:
    #                 # 调用 meterocr 进行 OCR 识别
    #                 ocr_result = meterocr(image)
    #
    #                 # 检查 OCR 结果
    #                 if ocr_result is not None and len(ocr_result) > 0:
    #                     # 清除上一次的显示结果
    #                     self.ui.text_meterocr_photo.clear()
    #
    #                     # 将识别结果逐行显示在 text_meterocr_photo 中
    #                     for line in ocr_result:
    #                         self.ui.text_meterocr_photo.append(line)
    #                 else:
    #                     # 如果 OCR 没有识别出任何内容
    #                     QMessageBox.warning(self, "OCR 识别", "未能识别出有效的文本，请尝试使用更清晰的图片。")
    #             else:
    #                 # 如果图片无法读取
    #                 QMessageBox.warning(self, "错误", "无法读取图片文件。")
    #         else:
    #             # 如果未选择图片
    #             QMessageBox.warning(self, "错误", "未选择图片文件！")
    #     except Exception as result:
    #         # 捕获 OCR 过程中发生的任何异常，并在日志中输出
    #         print(f"OCR 识别出错: {result}")
    #         QMessageBox.warning(self, "OCR 识别", "OCR 识别出错，请检查图片文件或尝试使用其他图片。")
    #
    #     # QMessageBox.critical(self, "错误", f"OCR 识别出错: {str(e)}")
    #
    # def performOcrOnCameraFrame(self):
    #     # 对显示在 canema_save 中的捕获图片进行 OCR 识别
    #     try:
    #         if self.captured_frame is not None:
    #             image = self.captured_frame  # 已捕获的帧
    #             # 使用 meterocr 进行识别
    #             meterocr.meterocr(image)
    #             # 将识别结果显示在 text_meterocr_camera 中
    #             self.display_text_camera()
    #         else:
    #             QMessageBox.warning(self, "错误", "未捕获图像！")
    #     except Exception as e:
    #
    #         QMessageBox.critical(self, "错误", f"OCR 识别出错: {str(e)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_position is not None:
            delta = event.globalPosition().toPoint() - self.old_position
            self.move(self.pos() + delta)
            self.old_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_position = None

    def startClock(self):
        # 初始化时间更新定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

    def updateTime(self):
        current_time = datetime.utcnow() + timedelta(hours=8)
        formatted_time = current_time.strftime("%Y/%m/%d 北京时间：%H/%M/%S")
        self.ui.time_label.setText(formatted_time)

    def saveUsers(self):
        # 保存用户信息到文件
        with open('users.txt', 'w') as f:
            for username, password in self.users.items():
                f.write(f"{username},{password}\n")

    def loadUsers(self):
        # 加载保存的用户数据，指定以 UTF-8 编码读取
        if os.path.exists("users.txt"):
            try:
                with open("users.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if "," in line:  # 检查是否包含":"
                            try:
                                username, password = line.split(",")
                                self.users[username] = password
                            except ValueError:
                                # 如果解析错误，跳过该行
                                print(f"跳过无效行: {line}")
                        else:
                            print(f"跳过格式错误行: {line}")
            except UnicodeDecodeError as e:
                print(f"编码错误: {e}")

    def display_text(self):
        file_path = "./result.txt"  # 指定文件路径
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("文件不存在或无法打开。")
            return
        # 显示文件内容
        self.ui.text_meterocr_photo.setPlainText(text)
    def display_text_camera(self):
        file_path = "./result.txt"  # 指定文件路径
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                text = file.read()
        except FileNotFoundError:
            print("文件不存在或无法打开。")
            return
        # 显示文件内容
        self.ui.text_meterocr_camera.setPlainText(text)

    def openImage(self):
        # 打开文件对话框，选择图片，并显示在界面上
        image_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            self.current_image_path = image_path
            pixmap = QPixmap(image_path)
            self.ui.image_board.setPixmap(pixmap)
            self.ui.image_board.setScaledContents(True)

    def performOcrOnPhoto(self):
        # 使用多线程处理图片OCR识别
        if self.current_image_path:
            image = cv2.imread(self.current_image_path)
            if image is not None:
                # 创建OCR处理线程
                self.ocr_thread = OcrThread(image)
                self.ocr_thread.ocr_finished.connect(self.display_text)  # 连接结果到显示函数
                self.ocr_thread.start()  # 启动线程
            else:
                QMessageBox.warning(self, "错误", "无法读取图片文件。")
        else:
            QMessageBox.warning(self, "错误", "未选择图片文件！")

    def performOcrOnCameraFrame(self):
        # 使用多线程处理摄像头帧OCR识别
        if self.captured_frame is not None:
            # 创建OCR处理线程
            self.ocr_thread = OcrThread(self.captured_frame, is_camera=True)
            self.ocr_thread.ocr_finished.connect(self.display_text_camera)  # 连接结果到显示函数
            self.ocr_thread.start()  # 启动线程
        else:
            QMessageBox.warning(self, "错误", "未捕获图像！")

    # def display_text_photo(self, text):
    #     # 显示OCR识别的文本结果
    #     self.ui.text_meterocr_photo.setPlainText(text)
    #
    # def display_text_camera(self, text):
    #     # 显示OCR识别的摄像头帧结果
    #     self.ui.text_meterocr_camera.setPlainText(text)

# def start_gui():
#     app = QApplication(sys.argv)
#     widget = gui()
#     widget.show()
#     sys.exit(app.exec())
#
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = gui()
    widget.show()
    sys.exit(app.exec())