# -*- coding: utf-8 -*-
import cv2
import detect
import numpy as np
from meterocr import *
from gui import *
from datetime import datetime
# 物理单位索引
import copy

dic_meter_unit = {
    '型号': ['型号', ''],
    'num': ['示数', ''],
    'ohm': ['欧姆', ''],
    'miu': ['(μ/m)A', ''],
    'mv': ['mV', ''],
    'nf': ['nf', ''],
    'hz': ['HZ', ''],
    'ad': ['AC/DC', ''],
    'am': ['A/M', ''],
    'word_corner': ['单位', ''],
    'num_corner': ['小数字', '']
}

# 确保在程序的初始化部分深拷贝字典
dic_unit_copy = copy.deepcopy(dic_meter_unit)



# dic_unit_copy = dic_meter_unit.copy()
# # 文件A的路径
# file_result_path = 'D:\\MvCamCtrlNet\\BasicDemo\\bin\\x64\\Debug\\result.txt'
# # 文件B的路径
# file_log_path = 'D:\\MvCamCtrlNet\\BasicDemo\\bin\\x64\\Debug\\log.txt'

# 文件A的路径
file_result_path = 'result.txt'
# 文件B的路径
file_log_path = 'log.txt'


class Axis:
    def __init__(self, axis_model, axis_left=0.0, axis_right=0.0, axis_up=0.0, axis_down=0.0):
        # 型号的x,y坐标
        self.axis_x1 = axis_model[0][0]
        self.axis_x2 = axis_model[2][0]
        self.axis_y1 = axis_model[0][1]
        self.axis_y2 = axis_model[2][1]
        # 上下左右的比例
        self.axis_left = axis_left
        self.axis_right = axis_right
        self.axis_up = axis_up
        self.axis_down = axis_down

    def get_axis_arr(self):  # 获取新框的坐标数据
        axis_arr = (
            int(self.axis_x1 + self.axis_left * (self.axis_x2 - self.axis_x1)),  # 左
            int(self.axis_y1 + self.axis_up * (self.axis_x2 - self.axis_x1)),  # 上
            int(self.axis_x2 + self.axis_right * (self.axis_x2 - self.axis_x1)),  # 右
            int(self.axis_y2 + self.axis_down * (self.axis_x2 - self.axis_x1))  # 下
        )
        return axis_arr


def read_txt_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")


# def res_store():
#     with open(file_result_path, 'a') as file:
#         for idx in dic_unit_copy:
#             file.write(dic_unit_copy[idx][0] + '\t: ' + dic_unit_copy[idx][1] + '\n')
#     with open(file_log_path, 'a') as file_log:
#         for idx in dic_unit_copy:
#             file_log.write(dic_unit_copy[idx][0] + '\t: ' + dic_unit_copy[idx][1] + '\n')



def res_store():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间并格式化为字符串
    with open(file_result_path, 'a') as file:
        file.write(f"识别时间：{current_time}\n")  # 将识别时间写入结果文件
        for idx in dic_unit_copy:
            file.write(dic_unit_copy[idx][0] + '\t: ' + dic_unit_copy[idx][1] + '\n')
    with open(file_log_path, 'a') as file_log:
        file_log.write(f"识别时间：{current_time}\n")  # 将识别时间写入日志文件
        for idx in dic_unit_copy:
            file_log.write(dic_unit_copy[idx][0] + '\t: ' + dic_unit_copy[idx][1] + '\n')

def replace_omega(s):
    if s.startswith(('k', 'K')):
        return 'KΩ'
    elif s.startswith('m'):
        return 'mΩ'
    elif s.startswith('M'):
        return 'MΩ'
    elif s.startswith(('g', 'G')):
        return 'GΩ'
    else:
        return 'Ω'


def unit_1_replace(unit_word_1):
    if unit_word_1 == '':
        unit_word_1 = ''
    elif unit_word_1 == 'k' or unit_word_1 == 'K':
        unit_word_1 = 'k'
    elif unit_word_1 == 'm':
        unit_word_1 = 'm'
    elif unit_word_1 == 'M':
        unit_word_1 = 'M'
    elif unit_word_1 == 'g' or unit_word_1 == 'G':
        unit_word_1 = 'G'
    elif unit_word_1 == 'n' or unit_word_1 == 'N':
        unit_word_1 = 'n'
    else:
        unit_word_1 = 'μ'
    return unit_word_1


def unit_2_replace(unit_word_2):
    if unit_word_2 in 'vV':
        unit_word_2 = 'V'
    elif unit_word_2 in 'aA':
        unit_word_2 = 'A'
    elif unit_word_2 in 'fF':
        unit_word_2 = 'F'
    return unit_word_2


# 图像二值化
def save_unit_1_2(unit_word_1, unit_word_2):
    if unit_word_1 != '':
        unit_word_1 = unit_1_replace(unit_word_1)
    if unit_word_2 != '':
        if unit_word_2 == 'f' or unit_word_2 == 'F':
            unit_word_2 = 'F'
            unit_word_1_2 = unit_word_1 + unit_word_2
            save_exist_text('nf', unit_word_1_2)
            save_exist_text('mv')
            save_exist_text('miu')
        elif unit_word_2 == 'v' or unit_word_2 == 'V':
            unit_word_2 = 'V'
            unit_word_1_2 = unit_word_1 + unit_word_2
            save_exist_text('nf')
            save_exist_text('mv', unit_word_1_2)
            save_exist_text('miu')
        elif unit_word_2 == 'a' or unit_word_2 == 'A':
            unit_word_2 = 'A'
            unit_word_1_2 = unit_word_1 + unit_word_2
            save_exist_text('nf')
            save_exist_text('mv')
            save_exist_text('miu', unit_word_1_2)
        elif unit_word_2.lower() == 'hz':
            unit_word_2 = 'HZ'
    else:
        save_exist_text('nf')
        save_exist_text('mv')
        save_exist_text('miu')


def img_binary(img_arr, thrshd_proportion=0.25):
    # 灰度化 RGB
    img_gray = 0.2126 * img_arr[:, :, 2] + 0.7152 * img_arr[:, :, 1] + 0.0722 * img_arr[:, :, 0]
    # 二值化
    img_max = img_gray.max()
    img_min = img_gray.min()
    thrshd = img_min + thrshd_proportion * (img_max - img_min)
    img_gray[img_gray >= thrshd] = 255
    img_gray[img_gray < thrshd] = 0
    img_arr[:, :, 0] = img_gray
    img_arr[:, :, 1] = img_gray
    img_arr[:, :, 2] = img_gray
    return img_arr


# 存储二值化图像
def img_store(img, axis_img, full_binary_path, binary=False, thrshd_proportion=0.5):
    img_arr = 255 * img[
                    int(axis_img.axis_y1 + axis_img.axis_up * (axis_img.axis_x2 - axis_img.axis_x1)):
                    int(axis_img.axis_y2 + axis_img.axis_down * (axis_img.axis_x2 - axis_img.axis_x1)),
                    int(axis_img.axis_x1 + axis_img.axis_left * (axis_img.axis_x2 - axis_img.axis_x1)):
                    int(axis_img.axis_x2 + axis_img.axis_right * (axis_img.axis_x2 - axis_img.axis_x1))
                    ]
    if binary:
        img_arr = img_binary(img_arr, thrshd_proportion=thrshd_proportion)
    cv2.imwrite(full_binary_path, img_arr)


def victor6800_yolo(full_binary_path):
    all_res = detect.detect_qianxing_number(full_binary_path)
    fina_res = ''.join(str(int(item[5])) if 0 <= int(item[5]) <= 9 else '' for item in all_res)
    return int(fina_res)


def table_yolo(full_binary_path):
    all_res = detect.detect_number(full_binary_path)
    fina_res = ''.join(str(int(item[5])) if 0 <= int(item[5]) <= 9 else '' for item in all_res)
    return int(fina_res)
# def table_yolo(full_binary_path):
#     all_res = detect.detect_number(full_binary_path)
#     fina_res_str = ''.join(
#         str(int(item[5])) if isinstance(item, str) and 0 <= int(item[5]) <= 9 else '' for item in all_res)
#
#     if fina_res_str:
#         return int(fina_res_str)
#     else:
#         return None  # 或者返回适当地默认值，取决于你的需求


# 小数点位置，存在flag里
def process_points(draw, img, axis_points, point_list, point_proportion=0.3, thrshd_proportion=0.4,is_draw=False):
    point_flag = 0
    for idx in range(len(point_list)):
        point_left = axis_points.axis_left + point_list[idx]
        point_right = axis_points.axis_right + point_list[idx]
        if is_draw == True:
            draw.rectangle((
                axis_points.axis_x1 + point_left * (axis_points.axis_x2 - axis_points.axis_x1),
                axis_points.axis_y1 + axis_points.axis_up * (axis_points.axis_x2 - axis_points.axis_x1),
                axis_points.axis_x2 + point_right * (axis_points.axis_x2 - axis_points.axis_x1),
                axis_points.axis_y2 + axis_points.axis_down * (axis_points.axis_x2 - axis_points.axis_x1)),
                outline='yellow', width=3)
        point_arr = 255 * img[
                          int(axis_points.axis_y1 + axis_points.axis_up * (axis_points.axis_x2 - axis_points.axis_x1)):
                          int(axis_points.axis_y2 + axis_points.axis_down * (
                                      axis_points.axis_x2 - axis_points.axis_x1)),
                          int(axis_points.axis_x1 + point_left * (axis_points.axis_x2 - axis_points.axis_x1)):
                          int(axis_points.axis_x2 + point_right * (axis_points.axis_x2 - axis_points.axis_x1))
                          ]
        point_arr = img_binary(point_arr, thrshd_proportion)
        pixel_black = np.sum(point_arr == 0)
        # 小数点占比
        print(f'小数点 {idx + 1} : {pixel_black / point_arr.size * 100:.1f}%')

        if pixel_black / point_arr.size > point_proportion:
            point_flag = idx + 1
            point_proportion = pixel_black / point_arr.size
            # img_test = Image.fromarray(point_arr.astype(np.uint8))
            # img_test.show()
    return point_flag


# 划分ocr区域
def get_roi_arr(draw, img, axis_words, binary=False, thrshd_proportion=0.25, is_draw=True):
    if is_draw == True:
        draw.rectangle((axis_words.get_axis_arr()), outline='blue', width=3)
    # 裁剪roi图像
    roi_arr = 255 * img[
                    int(axis_words.axis_y1 + axis_words.axis_up * (axis_words.axis_x2 - axis_words.axis_x1)):
                    int(axis_words.axis_y2 + axis_words.axis_down * (axis_words.axis_x2 - axis_words.axis_x1)),
                    int(axis_words.axis_x1 + axis_words.axis_left * (axis_words.axis_x2 - axis_words.axis_x1)):
                    int(axis_words.axis_x2 + axis_words.axis_right * (axis_words.axis_x2 - axis_words.axis_x1))
                    ]
    if binary:
        roi_arr = img_binary(roi_arr, thrshd_proportion=thrshd_proportion)
    height, width = roi_arr.shape[:2]
    roi_height = height + 1000
    roi_width = width + 1000
    new_roi_arr = np.ones((roi_height, roi_width, 3), np.uint8) * 255
    new_roi_arr[500:roi_height - 500, 500:roi_width - 500] = roi_arr
    return new_roi_arr


def save_mv(roi_show_res):
    unit_text = 'mV'
    if len(roi_show_res) != 0:
        dic_unit_copy['mv'][1] = roi_show_res[0][0]


def save_num_yolo(fina_res, point_flag):
    unit_text = '示数'
    if fina_res is not None:
        # >>>>>>>判断小数点位置>>>>>>>
        if point_flag == 1:
            word_text = str(fina_res / 1000)
        elif point_flag == 2:
            word_text = str(fina_res / 100)
        elif point_flag == 3:
            word_text = str(fina_res / 10)
        else:
            word_text = str(fina_res)

        dic_unit_copy['num'][1] = word_text


def save_num_ocr(roi_show_res, point_flag):
    if len(roi_show_res) != 0:
        # >>>>>>>判断小数点位置>>>>>>>
        word_text = roi_show_res[0][0].replace('.', '')
        if point_flag == 1:
            word_text = float(word_text) / 1000
        elif point_flag == 2:
            word_text = float(word_text) / 100
        elif point_flag == 3:
            word_text = float(word_text) / 10
        word_text = str(word_text)
        # <<<<<<<判断小数点位置<<<<<<<
        dic_unit_copy['num'][1] = word_text


def save_ohm(roi_show_res,point_ohm=0):
    if len(roi_show_res) != 0:
        word_text = replace_omega(roi_show_res[0][0])
    elif point_ohm != 0:
        word_text = ''
    elif point_ohm == 0:
        word_text = 'Ω'
    dic_unit_copy['ohm'][1] = word_text


def save_word_corner(roi_show_res):
    if len(roi_show_res) != 0:
        dic_unit_copy['word_corner'][1] = roi_show_res[0][0]


def save_num_corner(roi_show_res):
    if len(roi_show_res) != 0:
        dic_unit_copy['num_corner'][1] = roi_show_res[0][0]


def save_nf(roi_show_res):
    if len(roi_show_res) != 0:
        dic_unit_copy['nf'][1] = roi_show_res[0][0]


def save_hz(roi_show_res):
    if len(roi_show_res) != 0:
        dic_unit_copy['hz'][1] = roi_show_res[0][0]


def save_ac_dc(roi_show_res):
    unit_ac_dc = 'AC/DC'
    if len(roi_show_res) != 0:
        dic_unit_copy['ad'][1] = roi_show_res[0][0]


def save_auto_manual(roi_show_res):
    unit_text = 'A/M'
    if len(roi_show_res) != 0:
        dic_unit_copy['am'][1] = roi_show_res[0][0]


def save_miu_ma(roi_show_res):
    unit_text = '(μ/m)A'
    if len(roi_show_res) != 0:
        # 判断μA，mA，A
        if roi_show_res[0][0] == 'mA':
            word_text = 'mA'
        elif roi_show_res[0][0] == 'A':
            word_text = 'A'
        else:
            word_text = 'μA'
        # 存储结果
        dic_unit_copy['miu'][1] = word_text


# def save_exist_text(index, words=''):
#     dic_unit_copy[index][1] = words
def save_exist_text(index, words=''):
    global dic_unit_copy
    # 如果字典为空，重新初始化它
    if not dic_unit_copy:
        dic_unit_copy = copy.deepcopy(dic_meter_unit)

    print(f"Index: {index}, Words: {words}")
    print(dic_unit_copy)

    if index not in dic_unit_copy:
        dic_unit_copy[index] = ['']
    dic_unit_copy[index][1] = words



