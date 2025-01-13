
import os

import GUI2

os.environ['KMP_DUPLICATE_LIB_OK']='True'
import ctypes
import cv2
import meterocr
import matplotlib.pyplot as plt
import numpy as np


def main2():

    # image_d = 'D:\\data_project\\meterocr\\312\\Image_w5472_h3648_fn7307.bmp'
    # image = cv2.imread(image_d)
    #
    # # >>>旋转图像识别>>>
    # height, width = image.shape[:2]
    # rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
    # rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    # meterocr.meterocr(rotated_image)
    GUI2.start_GUI()

if __name__ == '__main__':

    main2()