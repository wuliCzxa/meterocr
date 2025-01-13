import cv2
import torch
from PIL import Image
from pytesseract import image_to_string
import numpy as np

# 加载YOLOv5模型
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # 可以替换为更大的模型如'yolov5m'或'yolov5l'

# 设置安全参数范围
安全参数范围 = {
    "警告灯": (0, 1),
    "错误代码": (0, 100)
}

# 实时监测与异常检测
def 实时监测与异常检测(frame):
    # 将OpenCV图像转换为PIL图像
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = Image.fromarray(frame)

    # 使用YOLOv5进行对象检测
    results = model(frame)

    # 获取检测结果
    df = results.pandas().xyxy[0]  # Dataframe格式

    # 检查异常
    for index, row in df.iterrows():
        类别 = row['name']
        置信度 = row['confidence']
        if 类别 in 安全参数范围 and 置信度 > 安全参数范围[类别][1]:
            触发警报(类别)

    # 使用OCR识别
    文本 = image_to_string(frame)
    if "错误代码" in 文本:
        触发警报("错误代码")

# 触发警报
def 触发警报(类型):
    print("发现异常情况：", 类型)

# 读取视频流并进行处理
cap = cv2.VideoCapture(0)

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        实时监测与异常检测(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()