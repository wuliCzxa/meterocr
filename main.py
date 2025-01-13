
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import ctypes
import cv2
import meterocr
import matplotlib.pyplot as plt
import numpy as np
import gui
def main():


    # img_test = '001.bmp'
    # image_d = 'D:\\' + img_test  # 替换为您的图片路径
    # # image_d = 'D:\\data_project\\' + img_test  # 替换为您的图片路径
    #
    #
    # image = cv2.imread(image_d)
    gui.start_gui()

    # >>>旋转图像识别>>>
    #height, width = image.shape[:2]
    #rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
    #rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    #meterocr.meterocr(rotated_image)
    # <<<旋转图像识别<<<

    # >>>非旋转图像识别>>>

    # <<<非旋转图像识别<<<

    # <<< 测试代码_1 <<<


    # 创建一个示例图像数据（这里使用随机数据）



    # # 获取工程主目录的绝对路径
    # project_dir = os.path.dirname(os.path.abspath(__file__))
    #
    # # 构建 .pyd 文件的完整路径
    # pyd_path = os.path.join(project_dir, 'output', 'meterocr.pyd')
    #
    # # 将 .pyd 文件所在的目录添加到 sys.path
    # sys.path.append(os.path.dirname(pyd_path))

    # 导入 .pyd 文件中的模块或函数

if __name__ == '__main__':
    main()
