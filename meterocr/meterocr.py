import os
import sys
import importlib
from types import ModuleType
#import paddle
import cv2
import logging
import numpy as np
from pathlib import Path
import sys
from tools.infer import predict_system
from ppocr.utils.logging import get_logger
from ppocr.utils.utility import check_and_read, get_image_file_list
from ppocr.utils.network import maybe_download, download_with_progressbar, is_link, confirm_model_dir_url
from tools.infer.utility import draw_ocr, str2bool, check_gpu
from ppstructure.utility import init_args, draw_structure_result
from ppstructure.predict_system import StructureSystem, save_structure_res, to_excel
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

import detect
import time

__dir__ = os.path.dirname(__file__)
sys.path.append(os.path.join(__dir__, ''))
tools = importlib.import_module('.', 'tools')
ppocr = importlib.import_module('.', 'ppocr')
ppstructure = importlib.import_module('.', 'ppstructure')
logger = get_logger()


SUPPORT_DET_MODEL = ['DB']
VERSION = '2.6.1.0'
SUPPORT_REC_MODEL = ['CRNN', 'SVTR_LCNet']
BASE_DIR = os.path.expanduser("~/.paddleocr/")

DEFAULT_OCR_MODEL_VERSION = 'PP-OCRv3'
SUPPORT_OCR_MODEL_VERSION = ['PP-OCRv3']


# 文件A的路径
file_result_path = 'result.txt'

# 文件B的路径
file_log_path = 'log.txt'

# 单次记录的内容
content_to_record = "这是要记录的内容。"

MODEL_URLS = {
    'OCR': {
        'PP-OCRv3': {
            'det': {
                'ch': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_det_infer.tar',
                },
                'en': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar',
                },
                'ml': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/Multilingual_PP-OCRv3_det_infer.tar'
                }
            },
            'rec': {
                'ch': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/ppocr_keys_v1.txt'
                },
                'en': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/en_dict.txt'
                },
                'korean': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/korean_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/korean_dict.txt'
                },
                'japan': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/japan_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/japan_dict.txt'
                },
                'chinese_cht': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/chinese_cht_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/chinese_cht_dict.txt'
                },
                'ta': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/ta_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/ta_dict.txt'
                },
                'te': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/te_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/te_dict.txt'
                },
                'ka': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/ka_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/ka_dict.txt'
                },
                'latin': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/latin_dict.txt'
                },
                'arabic': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/arabic_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/arabic_dict.txt'
                },
                'cyrillic': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/cyrillic_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/cyrillic_dict.txt'
                },
                'devanagari': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/devanagari_PP-OCRv3_rec_infer.tar',
                    'dict_path': './ppocr/utils/dict/devanagari_dict.txt'
                },
            },
            'cls': {
                'ch': {
                    'url':
                    'https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar',
                }
            },
        }
    }
}

# 位置标记类
class AxisProportion:
    def __init__(self, axis_left, axis_right, axis_up, axis_down):
        self.axis_left = axis_left
        self.axis_right = axis_right
        self.axis_up = axis_up
        self.axis_down = axis_down
# 小数点位置
class MarkPoint:
    def __init__(self, point_proportion = 0.15, thrshd_proportion = 0.25):
        self.point_proportion = point_proportion  # 像素占比
        self.thrshd_proportion = thrshd_proportion  # 二值化阈值
        self.point_flag = 0 # 判断小数点在哪个位置，0表示没有小数点

    def process_points(self, draw, img, axis_x1, axis_y1, axis_x2, axis_y2, points):
        for idx, point in enumerate(points, start=1):
            draw.rectangle((
                axis_x1 + point.axis_left * (axis_x2 - axis_x1),
                axis_y1 + point.axis_up * (axis_x2 - axis_x1),
                axis_x2 + point.axis_right * (axis_x2 - axis_x1),
                axis_y2 + point.axis_down * (axis_x2 - axis_x1)), outline='yellow', width=3)
            point_arr = 255 * img[
                              int(axis_y1 + point.axis_up * (axis_x2 - axis_x1)):
                              int(axis_y2 + point.axis_down * (axis_x2 - axis_x1)),
                              int(axis_x1 + point.axis_left * (axis_x2 - axis_x1)):
                              int(axis_x2 + point.axis_right * (axis_x2 - axis_x1))]
            y = 0.2126 * point_arr[:, :, 2] + 0.7152 * point_arr[:, :, 1] + 0.0722 * point_arr[:, :, 0]
            y_max = y.max()
            y_min = y.min()
            thrshd = y_min + self.thrshd_proportion * (y_max - y_min)

            y[y >= thrshd] = 255
            y[y < thrshd] = 0

            point_arr[:, :, 0] = y
            point_arr[:, :, 1] = y
            point_arr[:, :, 2] = y

            pixel_black = np.sum(point_arr == 0)
            print(f'小数点 {idx} - 黑像素: {pixel_black}')
            print(f'小数点 {idx} - 总像素: {point_arr.size}')
            print(f'小数点 {idx} - 像素比: {pixel_black / point_arr.size}')

            if pixel_black / point_arr.size > self.point_proportion:
                self.point_flag = idx
                self.point_proportion = pixel_black / point_arr.size
                print(self.point_flag)
                # img_test = Image.fromarray(point_arr.astype(np.uint8))
                # img_test.show()
        return self.point_flag

def mark_words(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, axis_words):
    draw.rectangle((
        axis_x1 + axis_words.axis_left * (axis_x2 - axis_x1),
        axis_y1 + axis_words.axis_up * (axis_x2 - axis_x1),
        axis_x2 + axis_words.axis_right * (axis_x2 - axis_x1),
        axis_y2 + axis_words.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)
    # 裁剪roi图像
    roi_arr = 255 * img[
                       int(axis_y1 + axis_words.axis_up * (axis_x2 - axis_x1)):
                       int(axis_y2 + axis_words.axis_down * (axis_x2 - axis_x1)),
                       int(axis_x1 + axis_words.axis_left * (axis_x2 - axis_x1)):
                       int(axis_x2 + axis_words.axis_right * (axis_x2 - axis_x1))]
    roi_height, roi_width = roi_arr.shape[:2]
    new_roi_height = roi_height + 1000
    new_roi_width = roi_width + 1000
    new_roi_arr = np.zeros((new_roi_height, new_roi_width, 3), np.uint8)

    new_roi_arr[500:new_roi_height - 500, 500:new_roi_width - 500] = roi_arr
    return new_roi_arr
    # >>>>>>>>>>>>>>>> mV >>>>>>>>>>>>>>>>>>>
def save_mv(roi_show_res):
    show_index = 0
    with open('result.txt', 'a') as file:
        file.write('mV' + '\t: ')
    with open('log.txt', 'a') as file_log:
        file_log.write('mV' + '\t: ')
        # <<<<<<<<<<<<<<<< mV <<<<<<<<<<<<<<<<<<<
        if len(roi_show_res) != 0:
            for show_index in range(0, len(roi_show_res[0]) - 1):
                with open('result.txt', 'a') as file:
                    file.write(roi_show_res[show_index][0] + '\n')
                with open('log.txt', 'a') as file_log:
                    file_log.write(roi_show_res[show_index][0] + '\n')
        else:
            with open('result.txt', 'a') as file:
                file.write('\n')
            with open('log.txt', 'a') as file_log:
                file_log.write('\n')
def save_num(fina_res, point_flag):
    with open('result.txt', 'a') as file:
        file.write('示数' + '\t' ': ')
    with open('log.txt', 'a') as file_log:
        file_log.write('示数' + '\t' ': ')
        # <<<<<<<<<<<<<<<< 示数 <<<<<<<<<<<<<<<<<<<

        # if len(roi_numshow_back_res) != 0:
        #     for numshow_index in range(0, len(roi_numshow_front_res[0]) - 1):
        if len(fina_res) != 0:
            fina_res.reverse()
            with open('result.txt', 'a') as file:
                # >>>>>>>判断小数点位置>>>>>>>
                num_res = ''.join(map(str, fina_res))
                # print(result)
                # print(float(num_res))
                if point_flag == 1:
                    num_res = float(num_res) / 1000
                elif point_flag == 2:
                    num_res = float(num_res) / 100
                elif point_flag == 3:
                    num_res = float(num_res) / 10
                num_res = str(num_res)
                point_flag = 0  #
                # <<<<<<<判断小数点位置<<<<<<<
                file.write(num_res + '\n')  # roi_numshow_res[numshow_index][0]
            with open('log.txt', 'a') as file_log:
                file_log.write(num_res + '\n')
        else:
            with open('result.txt', 'a') as file:
                file.write('\n')
            with open('log.txt', 'a') as file_log:
                file_log.write('\n')
def save_ohm(roi_show_res):
    show_index = 0
    with open('result.txt', 'a') as file:
        file.write('欧姆' + '\t: ')
    with open('log.txt', 'a') as file_log:
        file_log.write('欧姆' + '\t: ')
        # <<<<<<<<<<<<<<<< mV <<<<<<<<<<<<<<<<<<<
        if len(roi_show_res) != 0:
            for show_index in range(0, len(roi_show_res[0]) - 1):
                with open('result.txt', 'a') as file:
                    file.write(roi_show_res[show_index][0] + '\n')
                with open('log.txt', 'a') as file_log:
                    file_log.write(roi_show_res[show_index][0] + '\n')
        else:
            with open('result.txt', 'a') as file:
                file.write('\n')
            with open('log.txt', 'a') as file_log:
                file_log.write('\n')
def save_nf(roi_show_res):
    show_index = 0
    with open('result.txt', 'a') as file:
        file.write('nf' + '\t: ')
    with open('log.txt', 'a') as file_log:
        file_log.write('nf' + '\t: ')
        # <<<<<<<<<<<<<<<< mV <<<<<<<<<<<<<<<<<<<
        if len(roi_show_res) != 0:
            for show_index in range(0, len(roi_show_res[0]) - 1):
                with open('result.txt', 'a') as file:
                    file.write(roi_show_res[show_index][0] + '\n')
                with open('log.txt', 'a') as file_log:
                    file_log.write(roi_show_res[show_index][0] + '\n')
        else:
            with open('result.txt', 'a') as file:
                file.write('\n')
            with open('log.txt', 'a') as file_log:
                file_log.write('\n')

def parse_args(mMain=True):
    import argparse
    parser = init_args()
    parser.add_help = mMain
    parser.add_argument("--lang", type=str, default='ch')
    parser.add_argument("--det", type=str2bool, default=True)
    parser.add_argument("--rec", type=str2bool, default=True)
    parser.add_argument("--type", type=str, default='ocr')
    parser.add_argument(
        "--ocr_version",
        type=str,
        choices=SUPPORT_OCR_MODEL_VERSION,
        default='PP-OCRv3',
        help='OCR Model version, the current model support list is as follows: '
        '1. PP-OCRv3 Support Chinese and English detection and recognition model, and direction classifier model'
        '2. PP-OCRv2 Support Chinese detection and recognition model. '
        '3. PP-OCR support Chinese detection, recognition and direction classifier and multilingual recognition model.'
    )

    for action in parser._actions:
        if action.dest in [
                'rec_char_dict_path', 'table_char_dict_path', 'layout_dict_path'
        ]:
            action.default = None
    if mMain:
        return parser.parse_args()
    else:
        inference_args_dict = {}
        for action in parser._actions:
            inference_args_dict[action.dest] = action.default
        return argparse.Namespace(**inference_args_dict)

def parse_lang(lang):
    latin_lang = [
        'af', 'az', 'bs', 'cs', 'cy', 'da', 'de', 'es', 'et', 'fr', 'ga', 'hr',
        'hu', 'id', 'is', 'it', 'ku', 'la', 'lt', 'lv', 'mi', 'ms', 'mt', 'nl',
        'no', 'oc', 'pi', 'pl', 'pt', 'ro', 'rs_latin', 'sk', 'sl', 'sq', 'sv',
        'sw', 'tl', 'tr', 'uz', 'vi', 'french', 'german'
    ]
    arabic_lang = ['ar', 'fa', 'ug', 'ur']
    cyrillic_lang = [
        'ru', 'rs_cyrillic', 'be', 'bg', 'uk', 'mn', 'abq', 'ady', 'kbd', 'ava',
        'dar', 'inh', 'che', 'lbe', 'lez', 'tab'
    ]
    devanagari_lang = [
        'hi', 'mr', 'ne', 'bh', 'mai', 'ang', 'bho', 'mah', 'sck', 'new', 'gom',
        'sa', 'bgc'
    ]
    if lang in latin_lang:
        lang = "latin"
    elif lang in arabic_lang:
        lang = "arabic"
    elif lang in cyrillic_lang:
        lang = "cyrillic"
    elif lang in devanagari_lang:
        lang = "devanagari"

    assert lang in MODEL_URLS['OCR'][DEFAULT_OCR_MODEL_VERSION][
        'rec'], 'param lang must in {}, but got {}'.format(
            MODEL_URLS['OCR'][DEFAULT_OCR_MODEL_VERSION]['rec'].keys(), lang)
    if lang == "ch":
        det_lang = "ch"
    elif lang == 'structure':
        det_lang = 'structure'
    elif lang in ["en", "latin"]:
        det_lang = "en"
    else:
        det_lang = "ml"
    return lang, det_lang

def get_model_config(type, version, model_type, lang):
    if type == 'OCR':
        DEFAULT_MODEL_VERSION = DEFAULT_OCR_MODEL_VERSION
    else:
        raise NotImplementedError

    model_urls = MODEL_URLS[type]
    if version not in model_urls:
        version = DEFAULT_MODEL_VERSION
    if model_type not in model_urls[version]:
        if model_type in model_urls[DEFAULT_MODEL_VERSION]:
            version = DEFAULT_MODEL_VERSION
        else:
            logger.error('{} models is not support, we only support {}'.format(
                model_type, model_urls[DEFAULT_MODEL_VERSION].keys()))
            sys.exit(-1)

    if lang not in model_urls[version][model_type]:
        if lang in model_urls[DEFAULT_MODEL_VERSION][model_type]:
            version = DEFAULT_MODEL_VERSION
        else:
            logger.error(
                'lang {} is not support, we only support {} for {} models'.
                format(lang, model_urls[DEFAULT_MODEL_VERSION][model_type].keys(
                ), model_type))
            sys.exit(-1)
    return model_urls[version][model_type][lang]


def img_decode(content: bytes):
    np_arr = np.frombuffer(content, dtype=np.uint8)  # 将data以流的形式读入转化成ndarray对象
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # 将图像文件解码为OpenCV中的图像格式。


class PaddleOCR(predict_system.TextSystem):
    def __init__(self, **kwargs):
        """
        paddleocr package
        args:
            **kwargs: other params show in paddleocr --help
        """
        params = parse_args(mMain=False)
        params.__dict__.update(**kwargs)
        assert params.ocr_version in SUPPORT_OCR_MODEL_VERSION, "ocr_version must in {}, but get {}".format(
            SUPPORT_OCR_MODEL_VERSION, params.ocr_version)
        params.use_gpu = check_gpu(params.use_gpu)

        if not params.show_log:
            logger.setLevel(logging.INFO)
        self.use_angle_cls = params.use_angle_cls
        lang, det_lang = parse_lang(params.lang)

        # init model dir
        det_model_config = get_model_config('OCR', params.ocr_version, 'det',
                                            det_lang)
        params.det_model_dir, det_url = confirm_model_dir_url(
            params.det_model_dir,
            os.path.join(BASE_DIR, 'whl', 'det', det_lang),
            det_model_config['url'])
        rec_model_config = get_model_config('OCR', params.ocr_version, 'rec',
                                            lang)
        params.rec_model_dir, rec_url = confirm_model_dir_url(
            params.rec_model_dir,
            os.path.join(BASE_DIR, 'whl', 'rec', lang), rec_model_config['url'])
        cls_model_config = get_model_config('OCR', params.ocr_version, 'cls',
                                            'ch')
        params.cls_model_dir, cls_url = confirm_model_dir_url(
            params.cls_model_dir,
            os.path.join(BASE_DIR, 'whl', 'cls'), cls_model_config['url'])
        if params.ocr_version == 'PP-OCRv3':
            params.rec_image_shape = "3, 48, 320"
        else:
            params.rec_image_shape = "3, 32, 320"
        # download model if using paddle infer
        if not params.use_onnx:
            maybe_download(params.det_model_dir, det_url)
            maybe_download(params.rec_model_dir, rec_url)
            maybe_download(params.cls_model_dir, cls_url)

        if params.det_algorithm not in SUPPORT_DET_MODEL:
            logger.error('det_algorithm must in {}'.format(SUPPORT_DET_MODEL))
            sys.exit(0)
        if params.rec_algorithm not in SUPPORT_REC_MODEL:
            logger.error('rec_algorithm must in {}'.format(SUPPORT_REC_MODEL))
            sys.exit(0)

        if params.rec_char_dict_path is None:
            params.rec_char_dict_path = str(
                Path(__file__).parent / rec_model_config['dict_path'])

        logger.debug(params)
        # init det_model and rec_model
        super().__init__(params)
        self.page_num = params.page_num

    def ocr(self, image, det=True, rec=True, cls=True):


        lines = ['17B', 'null_definiion', 'null_definiion', 'null_definiion', 'null_definiion',         # 0-4 17Bmax
                 '15B+', 'null_definiion', 'null_definiion','null_definiion','null_definiion',          # 5-9 15B+
                 '1508 INSULATION TESTER', '1508 INSULATION TESTER', '1508 INSULATIONTESTER', 'null_definiion', 'null_definiion',     # 10-14 1508
                 '115C', 'null_definiion', 'null_definiion', 'null_definiion', 'null_definiion',        # 15-19 115c
                 '177CTRUERMSMULTIMETER', 'null_definiion', 'null_definiion', 'null_definiion', 'null_definiion',        # 20-24 177C
                 '312CLAMPMETER', 'null_definiion', 'null_definiion', 'null_definiion', 'null_definiion',         # 25-29 312CLAMPMETER
                 'KKYORITSU',   'KYORITSU', 'null_definiion', 'null_definiion', 'null_definiion', # 30-34 KKYORITSU
                 'DIGITALMEGOHM', 'DIGITAL MEGOHM', 'null_definiion', 'null_definiion', 'null_definiion',   # 35-39 数字兆欧表
                 '4000 Counts', '4000Counts', 'null_definiion', 'null_definiion', 'null_definiion',     # 40-44 4000counts
                 'VICTOR6800', 'VICIOR6800', 'VICTOR 6800', 'ICIOR 6800','ICIOR6800', 'CIOR6800',       # 45-49 victor6800
                 ]
        length_line = len(lines)

        assert isinstance(image, (np.ndarray, list, str, bytes))
        if isinstance(image, list) and det == True:
            logger.error('When input a list of images, det must be false')
            exit(0)
        if cls == True and self.use_angle_cls == False:
            logger.warning(
                'Since the angle classifier is not initialized, the angle classifier will not be uesd during the forward process'
            )

        img = image


        # for infer pdf file
        if isinstance(img, list):
            if self.page_num > len(img) or self.page_num == 0:
                self.page_num = len(img)
            imgs = img[:self.page_num]
        else:
            imgs = [img]
        if det and rec:
            ocr_res = []
            for idx, img in enumerate(imgs):
                # roi_num_res '01,UNI-T，0.98'
                dt_boxes, roi_num_res, _ = self.__call__(img, cls)  # roi_num_res[list_index][element_index]  element_index: 0 内容， 1 置信度

                # numpy 转 PIL
                img = img[:, :, [2, 1, 0]]
                img = (img - img.min()) / (img.max() - img.min())
                img_pil = Image.fromarray((img * 255).astype(np.uint8))
                #img_pil2 = img_pil.copy()
                #img_pil.show()

                draw = ImageDraw.Draw(img_pil)  #
                tmp_res = [ [box.tolist(), res] for box, res in zip(dt_boxes, roi_num_res)]
                length2 = len(roi_num_res)

                try:
                    with open(file_log_path, 'r') as file_log:
                        log_content = file_log.read()
                except FileNotFoundError:
                    log_content = ""

                index_res = 0
                index_line = 0


                for index_line in range(0, length_line):    # 类别字典
                    for index_res in range(0, length2):     # 全部识别出的文字框
                        #vds = lines[index_line]
                        if lines[index_line] in roi_num_res[index_res][0]:
                            class_index = index_line
                            axis_x1 = dt_boxes[index_res][0][0]
                            axis_x2 = dt_boxes[index_res][2][0]
                            axis_y1 = dt_boxes[index_res][0][1]
                            axis_y2 = dt_boxes[index_res][2][1]

                            with open('result.txt', 'w') as file:
                                file.truncate(0)
                            # 17B
                            if 0 <= class_index <= 4:

                                # >>>>>>>>>>>>>>>> 型号 >>>>>>>>>>>>>>>>>>>
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                with open('result.txt', 'a') as file:
                                    file.write('型号'+'\t' + ': FLUKE 17B MAX')
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('型号'+'\t' + ': FLUKE 17B MAX')
                                    file_log.write('\n')
                                # <<<<<<<<<<<<<<<< 型号 <<<<<<<<<<<<<<<<<<<

                                # 屏幕区域
                                screen_17b = AxisProportion(-0.5, 0, 0.15, 1)
                                draw.rectangle((axis_x1 + screen_17b.axis_left * (axis_x2-axis_x1),
                                                axis_y1 + screen_17b.axis_up * (axis_x2-axis_x1),
                                                axis_x2 + screen_17b.axis_right * (axis_x2-axis_x1),
                                                axis_y2 + screen_17b.axis_down * (axis_x2-axis_x1)), outline='red', width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.15, -1.1, 0.88, 0.9),
                                    AxisProportion(0.15, -0.8, 0.88, 0.9),
                                    AxisProportion(0.45, -0.5, 0.88, 0.9)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                                fina_res = []
                                all_res = detect.detect_number()
                                for i in range(all_res.__len__()):
                                    if int(all_res[i][5]) == 2:
                                        fina_res.append(1)
                                    elif int(all_res[i][5]) == 1:
                                        fina_res.append(9)
                                    elif int(all_res[i][5]) == 3:
                                        fina_res.append(0)
                                    elif int(all_res[i][5]) == 4:
                                        fina_res.append(8)
                                    elif int(all_res[i][5]) == 5:
                                        fina_res.append(3)
                                    elif int(all_res[i][5]) == 6:
                                        fina_res.append(4)
                                    elif int(all_res[i][5]) == 7:
                                        fina_res.append(2)
                                    elif int(all_res[i][5]) == 8:
                                        fina_res.append(7)
                                    elif int(all_res[i][5]) == 9:
                                        fina_res.append(5)
                                    elif int(all_res[i][5]) == 0:
                                        fina_res.append(6)

                                # >>>>>>>>>>>>>>>> 示数 >>>>>>>>>>>>>>>>>>>
                                save_num(fina_res,point_flag)

                                # MΩ 区域
                                ohm_17b = AxisProportion(0.6, -0.1, 0.3, 0.37)
                                new_roi_arr = mark_words(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, ohm_17b)
                                roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                                save_ohm(roi_show_res)
                                # roi_Momega_arr = 255 * img[
                                #                     int(axis_y1 + Momega_17b.axis_up * (
                                #                             axis_x2 - axis_x1)):
                                #                     int(axis_y2 + Momega_17b.axis_down * (
                                #                             axis_x2 - axis_x1)),
                                #                     int(axis_x1 + Momega_17b.axis_left * (
                                #                             axis_x2 - axis_x1)):
                                #                     int(axis_x2 + Momega_17b.axis_right * (
                                #                             axis_x2 - axis_x1))]
                                # # roi_Momega高宽
                                # roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]
                                #
                                # new_roi_Momega_height = roi_Momega_height + 1000
                                # new_roi_Momega_width = roi_Momega_width + 1000
                                # new_roi_Momega_arr = np.zeros(
                                #     (new_roi_Momega_height, new_roi_Momega_width, 3), np.uint8)
                                #
                                # new_roi_Momega_arr[500:new_roi_Momega_height - 500,500:new_roi_Momega_width - 500] = roi_Momega_arr
                                #
                                # roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                # Momegashow_index = 0
                                #
                                # # detect.detect_omega()
                                #
                                # # >>>>>>>>>>>>>>>> 欧姆 >>>>>>>>>>>>>>>>>>>
                                # with open('result.txt', 'a') as file:
                                #     file.write('欧  姆：' + ' ')
                                # with open('log.txt', 'a') as file_log:
                                #     file_log.write('欧  姆：' + ' ')
                                # # <<<<<<<<<<<<<<<< 欧姆 <<<<<<<<<<<<<<<<<<<
                                #
                                #     if len(roi_Momegashow_res) != 0:
                                #         for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                #             with open('result.txt', 'a') as file:
                                #                 file.write(roi_Momegashow_res[Momegashow_index][
                                #                                0] + '\n')  # roi_numshow_res[numshow_index][0]
                                #             with open('log.txt', 'a') as file_log:
                                #                 file_log.write(
                                #                     roi_Momegashow_res[Momegashow_index][0] + '\n')
                                #     else:
                                #         with open('result.txt', 'a') as file:
                                #             file.write('\n')
                                #         with open('log.txt', 'a') as file_log:
                                #             file_log.write('\n')
                                #
                                # #######################################################################################################################################################
                                # roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]
                                #
                                # new_roi_Momega_height = roi_Momega_height + 1000
                                # new_roi_Momega_width = roi_Momega_width + 1000
                                # new_roi_Momega_arr = np.zeros((new_roi_Momega_height, new_roi_Momega_width, 3), np.uint8)
                                #
                                # new_roi_Momega_arr[500:new_roi_Momega_height-500, 500:new_roi_Momega_width-500] = roi_Momega_arr
                                #
                                # roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                # Momegashow_index = 0

                                # detect.detect_omega()

                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                # with open('result.txt', 'a') as file:
                                #     file.write('欧米伽：' + ' ')
                                # with open('log.txt', 'a') as file_log:
                                #     file_log.write('欧米伽：' + ' ')
                                # # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                #
                                #
                                #     if len(roi_Momegashow_res) != 0:
                                #         for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                #             with open('result.txt', 'a') as file:
                                #                 file.write(roi_Momegashow_res[Momegashow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                #             with open('log.txt', 'a') as file_log:
                                #                 file_log.write(roi_Momegashow_res[Momegashow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                #
                                #     else:
                                #         with open('result.txt', 'a') as file:
                                #             file.write('\n')
                                #         with open('log.txt', 'a') as file_log:
                                #             file_log.write('\n')

                                #######################################################################################################################################################
                                # nF 区域
                                nf_17b = AxisProportion(-0.2, 0, 0.45, 0.57)
                                new_roi_arr = mark_words(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, nf_17b)
                                roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                                save_nf(roi_show_res)
#                                 draw.rectangle((axis_x2 + nF_17b.axis_left * (axis_x2 - axis_x1),
#                                                 axis_y1 + nF_17b.axis_up * (axis_x2 - axis_x1),
#                                                 axis_x2 + nF_17b.axis_right * (axis_x2 - axis_x1),
#                                                 axis_y1 + nF_17b.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)
#
#                                 # 裁剪ROI图像
#                                 roi_nF_arr = 255*img[
#                                                  int(axis_y1 + nF_17b.axis_up * (axis_x2 - axis_x1)):int(axis_y1 + nF_17b.axis_down * (axis_x2 - axis_x1)),
#                                                  int(axis_x2 + nF_17b.axis_left * (axis_x2 - axis_x1)):int(axis_x2 + nF_17b.axis_right * (axis_x2 - axis_x1))]
#
# #######################################################################################################################################################
#                                 roi_nF_height, roi_nF_width = roi_nF_arr.shape[:2]
#
#                                 new_roi_nF_height = roi_nF_height + 1000
#                                 new_roi_nF_width = roi_nF_width + 1000
#                                 new_roi_nF_arr = np.zeros((new_roi_nF_height, new_roi_nF_width, 3), np.uint8)
#
#                                 new_roi_nF_arr[500:new_roi_nF_height - 500, 500:new_roi_nF_width - 500] = roi_nF_arr
#
#                                 roi_nF_boxes, roi_nFshow_res, _ = self.__call__(new_roi_nF_arr, cls)
#                                 nFshow_index = 0
#
#                                 with open('result.txt', 'a') as file:
#                                     file.write('  nf  ：' + ' ')
#                                 with open('log.txt', 'a') as file_log:
#                                     file_log.write('  nf  ：' + ' ')
#                                     if len(roi_nFshow_res) != 0:
#                                         for nFshow_index in range(0, len(roi_nFshow_res[0]) - 1):
#                                             with open('result.txt', 'a') as file:
#                                                 file.write(roi_nFshow_res[nFshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
#                                             with open('log.txt', 'a') as file_log:
#                                                 file_log.write(roi_nFshow_res[nFshow_index][0] + '\n')
#                                     else:
#                                         with open('result.txt', 'a') as file:
#                                             file.write('\n')
#                                         with open('log.txt', 'a') as file_log:
#                                             file_log.write('\n')
#

                                # >>>>>>>>>>>mv 区域>>>>>>>>>>
                                mv_17b = AxisProportion(0.78, 0, 0.57, 0.60)
                                new_roi_arr = mark_words(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, mv_17b)
                                roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                                save_mv(roi_show_res)
                                # <<<<<<<<<<<mv 区域<<<<<<<<<<

#######################################################################################################################################################

                                # AC、DC 区域
                                ad_17b = AxisProportion(-0.2, 0, 0.67, 0.78)
                                draw.rectangle((axis_x2 + ad_17b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_17b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_17b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_17b.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)

                                # 裁剪ROI图像
                                roi_AD_arr = 255*img[int(axis_y1 + ad_17b.axis_up * (axis_x2 - axis_x1)):int( axis_y2 + ad_17b.axis_down * (axis_x2 - axis_x1)),
                                                 int(axis_x2 + ad_17b.axis_left * (axis_x2 - axis_x1)):int(axis_x2 + ad_17b.axis_right * (axis_x2 - axis_x1))]

#######################################################################################################################################################
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]

                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                # >>>>>>>>>>>>>>>> A/D >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                # <<<<<<<<<<<<<<<< A/D <<<<<<<<<<<<<<<<<<<

                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

#######################################################################################################################################################

                                #μ 区域
                                miu_17b = AxisProportion(-0.25, 0, 0.78, 0.9)
                                draw.rectangle((axis_x2 + miu_17b.axis_left * (axis_x2 - axis_x1),
                                                axis_y2 + miu_17b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + miu_17b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + miu_17b.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)

                                # 裁剪ROI图像
                                roi_miu_arr = 255 * img[
                                                    int(axis_y2 + miu_17b.axis_up * (axis_x2 - axis_x1)):int(axis_y2 + miu_17b.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x2 + miu_17b.axis_left * (axis_x2 - axis_x1)):int(axis_x2 + miu_17b.axis_right * (axis_x2 - axis_x1))]

#######################################################################################################################################################
                                roi_miu_height, roi_miu_width = roi_miu_arr.shape[:2]

                                new_roi_miu_height = roi_miu_height + 1000
                                new_roi_miu_width = roi_miu_width + 1000
                                new_roi_miu_arr = np.zeros((new_roi_miu_height, new_roi_miu_width, 3), np.uint8)

                                new_roi_miu_arr[500:new_roi_miu_height - 500, 500:new_roi_miu_width - 500] = roi_miu_arr

                                roi_miu_boxes, roi_miushow_res, _ = self.__call__(new_roi_miu_arr, cls)
                                miushow_index = 0

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<

                                    if len(roi_miushow_res) != 0:
                                        for miushow_index in range(0, len(roi_miushow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                if roi_miushow_res[miushow_index][0] =='mA':
                                                    file.write('mA' + '\n')
                                                elif roi_miushow_res[miushow_index][0] =='A':
                                                    file.write('A' + '\n')
                                                else:
                                                    file.write('μA' + '\n')
                                            with open('log.txt', 'a') as file_log:
                                                # file_log.write(roi_miushow_res[miushow_index][0] + '\n')
                                                if roi_miushow_res[miushow_index][0] =='mA':
                                                    file_log.write('mA' + '\n')
                                                elif roi_miushow_res[miushow_index][0] =='A':
                                                    file_log.write('A' + '\n')
                                                else:
                                                    file_log.write('μA' + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

#######################################################################################################################################################

                                # A/M 区域
                                am_17b = AxisProportion(0, -0.45, 0.9, 1)
                                draw.rectangle((axis_x1 + am_17b.axis_left * (axis_x2 - axis_x1),
                                                axis_y2 + am_17b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_17b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_17b.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)

                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y2 + am_17b.axis_up * (axis_x2 - axis_x1)):int(axis_y2 + am_17b.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_17b.axis_left * (axis_x2 - axis_x1)):int( axis_x2 + am_17b.axis_right * (axis_x2 - axis_x1))]

#######################################################################################################################################################
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]

                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                # >>>>>>>>>>>>>>>> A/M >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                # <<<<<<<<<<<<<<<< A/M <<<<<<<<<<<<<<<<<<<

                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # >>>>>>>>>>>>>>>> (m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (m)A  ：' + ' ')
                                # <<<<<<<<<<<<<<<< (m)A <<<<<<<<<<<<<<<<<<<
                                import datetime
                                x = datetime.datetime.now()
                                name_image = str(x)
                                img_pil.show()
                                # img_pil.save('D:\\Desktop\\res\\'+name_image[21:-1]+'.bmp')
                                # img_pil.save('D:\\Desktop\\res\\17B_result.bmp')

                            # 15B+
                            elif 5 <= class_index <= 9:
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                # 屏幕区域
                                screen_15b = AxisProportion(-0.60, 0.10, 0.15, 1.2)
                                draw.rectangle((axis_x1 + screen_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_15b.axis_down * (axis_x2 - axis_x1)), outline='red', width=3)
                                # 小数点
                                points = [
                                    AxisProportion(-0.22, -1.12, 0.97, 1.02),
                                    AxisProportion(0.12, -0.78, 0.97, 1.02),
                                    AxisProportion(0.46, -0.44, 0.97, 1.02)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, points)

                                # 示数区域


                                num_15b = AxisProportion(- 0.58, -0.13, 0.48, 1.03)
                                draw.rectangle((axis_x1 + num_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_15b.axis_down * (axis_x2 - axis_x1)), outline='red',width=3)  # 11.1

                                # 裁剪ROI图像
                                roi_num_arr = 255 * img[int(axis_y1 + num_15b.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + num_15b.axis_down * (axis_x2 - axis_x1)),
                                                        int(axis_x1 + num_15b.axis_left * (axis_x2 - axis_x1)):
                                                        int(axis_x2 + num_15b.axis_right * (axis_x2 - axis_x1))]

                                # roi_num高宽
                                roi_num_height, roi_num_width = roi_num_arr.shape[:2]

                                # 给ROi一个宽度为500的外框
                                new_roi_num_height = roi_num_height + 1000
                                new_roi_num_width = roi_num_width + 1000
                                new_roi_num_arr = np.zeros((new_roi_num_height, new_roi_num_width, 3), np.uint8)
                                new_roi_num_arr[500:new_roi_num_height - 500, 500:new_roi_num_width - 500] = roi_num_arr


                                roi_num_boxes, roi_numshow_res, _ = self.__call__(new_roi_num_arr, cls)
                                numshow_index = 0
                                fina_res = []
                                all_res = detect.detect_number()
                                for i in range(all_res.__len__()):
                                    if int(all_res[i][5]) == 2:
                                        fina_res.append(1)
                                    elif int(all_res[i][5]) == 1:
                                        fina_res.append(9)
                                    elif int(all_res[i][5]) == 3:
                                        fina_res.append(0)
                                    elif int(all_res[i][5]) == 4:
                                        fina_res.append(8)
                                    elif int(all_res[i][5]) == 5:
                                        fina_res.append(3)
                                    elif int(all_res[i][5]) == 6:
                                        fina_res.append(4)
                                    elif int(all_res[i][5]) == 7:
                                        fina_res.append(2)
                                    elif int(all_res[i][5]) == 8:
                                        fina_res.append(7)
                                    elif int(all_res[i][5]) == 9:
                                        fina_res.append(5)
                                    elif int(all_res[i][5]) == 0:
                                        fina_res.append(6)

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型   号：FLUKE 15B+ ' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型   号：FLUKE 15B+' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(fina_res) != 0:
                                        fina_res.reverse()
                                        with open('result.txt', 'a') as file:
                                            # >>>>>>>判断小数点位置>>>>>>>
                                            num_res = ''.join(map(str, fina_res))
                                            # print(result)
                                            # print(float(num_res))
                                            if point_flag == 1:
                                                num_res = float(num_res) / 1000
                                            elif point_flag == 2:
                                                num_res = float(num_res) / 100
                                            elif point_flag == 3:
                                                num_res = float(num_res) / 10
                                            num_res = str(num_res)
                                            point_flag = 0  #
                                            # <<<<<<<判断小数点位置<<<<<<<
                                            file.write(num_res + '\n')    # roi_numshow_res[numshow_index][0]
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write(num_res + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                ######################################################################################################################################################
                                # MΩ 区域
                                Momega_15b = AxisProportion(0.6, -0.04, 0.35, 0.43)
                                draw.rectangle((axis_x1 + Momega_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + Momega_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + Momega_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + Momega_15b.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)
                                # 裁剪ROI图像
                                roi_Momega_arr = 255 * img[int(axis_y1 + Momega_15b.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + Momega_15b.axis_down * (axis_x2 - axis_x1)),
                                                        int(axis_x1 + Momega_15b.axis_left * (axis_x2 - axis_x1)):
                                                        int(axis_x2 + Momega_15b.axis_right * (axis_x2 - axis_x1))]

                                # roi_Momega高宽
                                roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]

                                new_roi_Momega_height = roi_Momega_height + 1000
                                new_roi_Momega_width = roi_Momega_width + 1000
                                new_roi_Momega_arr = np.zeros((new_roi_Momega_height, new_roi_Momega_width, 3),np.uint8)

                                new_roi_Momega_arr[500:new_roi_Momega_height - 500,
                                500:new_roi_Momega_width - 500] = roi_Momega_arr

                                roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                Momegashow_index = 0

                                # detect.detect_omega()

                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                    if len(roi_Momegashow_res) != 0:
                                        for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_Momegashow_res[Momegashow_index][0] + '\n')
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_Momegashow_res[Momegashow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧米伽：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧米伽：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> nf >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  nf  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  nf  ：' + ' ')
                                # <<<<<<<<<<<<<<<< nf <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                #######################################################################################################################################################
                                # mV区域
                                mV_15b = AxisProportion(0.87, 0.06, 0.64, 0.70)
                                draw.rectangle((axis_x1 + mV_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + mV_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + mV_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + mV_15b.axis_down * (axis_x2 - axis_x1)), outline='blue', width=3)
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + mV_15b.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + mV_15b.axis_down * (axis_x2 - axis_x1)),
                                                        int(axis_x1 + mV_15b.axis_left * (axis_x2 - axis_x1)):
                                                        int(axis_x2 + mV_15b.axis_right * (axis_x2 - axis_x1))]

                                # roi_mV高宽
                                roi_mV_height, roi_mV_width = roi_mV_arr.shape[:2]
                                # 500外框
                                new_roi_mV_height = roi_mV_height + 1000
                                new_roi_mV_width = roi_mV_width + 1000
                                new_roi_mV_arr = np.zeros((new_roi_mV_height, new_roi_mV_width, 3),
                                                          np.uint8)

                                new_roi_mV_arr[500:new_roi_mV_height - 500,
                                500:new_roi_mV_width - 500] = roi_mV_arr

                                roi_mV_boxes, roi_mVshow_res, _ = self.__call__(new_roi_mV_arr, cls)
                                mVshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                    if len(roi_mVshow_res) != 0:
                                        for mVshow_index in range(0, len(roi_mVshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mVshow_res[mVshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mVshow_res[mVshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # AC、DC 区域
                                ad_15b = AxisProportion(0.88, 0.06, 0.75, 0.90)
                                draw.rectangle((axis_x1 + ad_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_15b.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AD_arr = 255 * img[int(axis_y1 + ad_15b.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_15b.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_15b.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_15b.axis_right * (axis_x2 - axis_x1))]

                                # roi_AD高宽
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]
                                # 500外框
                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # μmA 区域
                                miu_15b = AxisProportion(0.81, 0.05, 0.93, 1.0)
                                draw.rectangle((axis_x1 + miu_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + miu_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + miu_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + miu_15b.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_miu_arr = 255 * img[int(axis_y1 + miu_15b.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + miu_15b.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + miu_15b.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + miu_15b.axis_right * (axis_x2 - axis_x1))]

                                # roi_miu高宽
                                roi_miu_height, roi_miu_width = roi_miu_arr.shape[:2]
                                # 500外框
                                new_roi_miu_height = roi_miu_height + 1000
                                new_roi_miu_width = roi_miu_width + 1000
                                new_roi_miu_arr = np.zeros((new_roi_miu_height, new_roi_miu_width, 3), np.uint8)

                                new_roi_miu_arr[500:new_roi_miu_height - 500, 500:new_roi_miu_width - 500] = roi_miu_arr

                                roi_miu_boxes, roi_miushow_res, _ = self.__call__(new_roi_miu_arr, cls)
                                miushow_index = 0

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<
                                    if len(roi_miushow_res) != 0:
                                        for miushow_index in range(0, len(roi_miushow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                if roi_miushow_res[miushow_index][0] =='mA':
                                                    file.write('mA' + '\n')
                                                elif roi_miushow_res[miushow_index][0] =='A':
                                                    file.write('A' + '\n')
                                                else:
                                                    file.write('μA' + '\n')
                                            with open('log.txt', 'a') as file_log:
                                                # file_log.write(roi_miushow_res[miushow_index][0] + '\n')
                                                if roi_miushow_res[miushow_index][0] =='mA':
                                                    file_log.write('mA' + '\n')
                                                elif roi_miushow_res[miushow_index][0] =='A':
                                                    file_log.write('A' + '\n')
                                                else:
                                                    file_log.write('μA' + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # A/M 区域
                                am_15b = AxisProportion(-0.12, -0.46, 1.08, 1.14)
                                draw.rectangle((axis_x1 + am_15b.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + am_15b.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_15b.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_15b.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y1 + am_15b.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + am_15b.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_15b.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + am_15b.axis_right * (axis_x2 - axis_x1))]

                                # roi_AM高宽
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]

                                # 500外框
                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                ######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # 1508 IN
                            elif 10 <= class_index <= 14:
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                # 屏幕区域
                                screen_1508 = AxisProportion(-0.55, 0.13, 0.16, 1.2)
                                draw.rectangle((axis_x1 + screen_1508.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_1508.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_1508.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_1508.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.13, -1.05, 0.68, 0.7),
                                    AxisProportion(0.12, -0.8, 0.68, 0.7),
                                    AxisProportion(0.4, -0.52, 0.68, 0.7)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2,
                                                                           axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<
                                # 示数区域
                                num_1508 = AxisProportion(-0.3, -0.32, 0.35, 0.68)
                                draw.rectangle((axis_x1 + num_1508.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_1508.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_1508.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_1508.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)

                                fina_res = []
                                all_res = detect.detect_number()
                                for i in range(all_res.__len__()):
                                    if int(all_res[i][5]) == 2:
                                        fina_res.append(1)
                                    elif int(all_res[i][5]) == 1:
                                        fina_res.append(9)
                                    elif int(all_res[i][5]) == 3:
                                        fina_res.append(0)
                                    elif int(all_res[i][5]) == 4:
                                        fina_res.append(8)
                                    elif int(all_res[i][5]) == 5:
                                        fina_res.append(3)
                                    elif int(all_res[i][5]) == 6:
                                        fina_res.append(4)
                                    elif int(all_res[i][5]) == 7:
                                        fina_res.append(2)
                                    elif int(all_res[i][5]) == 8:
                                        fina_res.append(7)
                                    elif int(all_res[i][5]) == 9:
                                        fina_res.append(5)
                                    elif int(all_res[i][5]) == 0:
                                        fina_res.append(6)

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型   号：FLUKE 1508' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型   号：FLUKE 1508' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(fina_res) != 0:
                                        fina_res.reverse()
                                        with open('result.txt', 'a') as file:
                                            # >>>>>>>判断小数点位置>>>>>>>
                                            num_res = ''.join(map(str, fina_res))
                                            if point_flag == 1:
                                                num_res = float(num_res) / 1000
                                            elif point_flag == 2:
                                                num_res = float(num_res) / 100
                                            elif point_flag == 3:
                                                num_res = float(num_res) / 10
                                            num_res = str(num_res)
                                            point_flag = 0  #
                                            # <<<<<<<判断小数点位置<<<<<<<
                                            file.write(num_res + '\n')  # roi_numshow_res[numshow_index][0]
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write(num_res + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # MΩ 区域
                                Momega_1508 = AxisProportion(0.8, 0.1, 0.44, 0.46)

                                draw.rectangle((axis_x1 + Momega_1508.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + Momega_1508.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + Momega_1508.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + Momega_1508.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_Momega_arr = 255 * img[int(axis_y1 + Momega_1508.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + Momega_1508.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + Momega_1508.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + Momega_1508.axis_right * (axis_x2 - axis_x1))]

                                # roi_Momega高宽
                                roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]

                                # 500外框
                                new_roi_Momega_height = roi_Momega_height + 1000
                                new_roi_Momega_width = roi_Momega_width + 1000
                                new_roi_Momega_arr = np.zeros((new_roi_Momega_height, new_roi_Momega_width, 3),np.uint8)

                                new_roi_Momega_arr[500:new_roi_Momega_height - 500,
                                                   500:new_roi_Momega_width - 500] = roi_Momega_arr

                                roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                Momegashow_index = 0

                                # detect.detect_omega()

                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                    if len(roi_Momegashow_res) != 0:
                                        for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_Momegashow_res[Momegashow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_Momegashow_res[Momegashow_index][0] + '\n')

                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # VAC、VDC 区域
                                ad_1508 = AxisProportion(0.8, 0.1, 0.54, 0.65)

                                draw.rectangle((axis_x1 + ad_1508.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_1508.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_1508.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_1508.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)
                                # 裁剪ROI图像
                                roi_Ad_arr = 255 * img[int(axis_y1 + ad_1508.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_1508.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_1508.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_1508.axis_right * (axis_x2 - axis_x1))]

                                # roi_VAD高宽
                                roi_VAD_height, roi_VAD_width = roi_Ad_arr.shape[:2]

                                # 500外框
                                new_roi_VAD_height = roi_VAD_height + 1000
                                new_roi_VAD_width = roi_VAD_width + 1000
                                new_roi_VAD_arr = np.zeros((new_roi_VAD_height, new_roi_VAD_width, 3), np.uint8)

                                new_roi_VAD_arr[500:new_roi_VAD_height - 500, 500:new_roi_VAD_width - 500] = roi_Ad_arr

                                roi_VAD_boxes, roi_VADshow_res, _ = self.__call__(new_roi_VAD_arr, cls)
                                VADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' VA/VD ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' VA/VD ：' + ' ')
                                    if len(roi_VADshow_res) != 0:
                                        for VADshow_index in range(0, len(roi_VADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_VADshow_res[VADshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_VADshow_res[VADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # 右下角小数字区域
                                numRcorner_1508 = AxisProportion(0.7, -0.1, 1., 1.2)

                                draw.rectangle((axis_x1 + numRcorner_1508.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + numRcorner_1508.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + numRcorner_1508.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + numRcorner_1508.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_numRcorner_arr = 255 * img[int(axis_y1 + numRcorner_1508.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + numRcorner_1508.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + numRcorner_1508.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + numRcorner_1508.axis_right * (axis_x2 - axis_x1))]

                                # roi_numRcorner高宽
                                roi_numRcorner_height, roi_numRcorner_width = roi_numRcorner_arr.shape[:2]
                                # 500外框
                                new_roi_numRcorner_height = roi_numRcorner_height + 1000
                                new_roi_numRcorner_width = roi_numRcorner_width + 1000
                                new_roi_numRcorner_arr = np.zeros((new_roi_numRcorner_height, new_roi_numRcorner_width, 3), np.uint8)

                                new_roi_numRcorner_arr[500:new_roi_numRcorner_height - 500, 500:new_roi_numRcorner_width - 500] = roi_numRcorner_arr

                                roi_numRcorner_boxes, roi_numRcornershow_res, _ = self.__call__(new_roi_numRcorner_arr, cls)
                                numRcornershow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' 右下数字  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' 右下数字  ：' + ' ')
                                    if len(roi_numRcornershow_res) != 0:
                                        for numRcornershow_index in range(0, len(roi_numRcornershow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_numRcornershow_res[numRcornershow_index][0] + '\n')  # roi_numRcornershow_res[numRcornershow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_numRcornershow_res[numRcornershow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                wordRcorner_1508 = AxisProportion(0.9, 0.1, 1., 1.2)

                                draw.rectangle((axis_x1 + wordRcorner_1508.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + wordRcorner_1508.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + wordRcorner_1508.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + wordRcorner_1508.axis_down * (axis_x2 - axis_x1)),
                                               outline='blue',
                                               width=3)
                                #######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # 115C
                            elif 15 <= class_index <= 19:
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                # 屏幕区域
                                screen_115c = AxisProportion(-2.24, 3.16, 0.7, 3.36)

                                draw.rectangle((axis_x1 + screen_115c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_115c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_115c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_115c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.61, -1.39, 2.68, 2.65),
                                    AxisProportion(0.55, -0.23, 2.68, 2.65),
                                    AxisProportion(1.7, 0.92, 2.68, 2.65)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2,
                                                                           axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                                # 示数区域
                                num_115c = AxisProportion(-2.24, 1.9, 1.14, 2.57)

                                draw.rectangle((axis_x1 + num_115c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_115c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_115c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_115c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)

                                fina_res = []
                                all_res = detect.detect_number()
                                for i in range(all_res.__len__()):
                                    if int(all_res[i][5]) == 2:
                                        fina_res.append(1)
                                    elif int(all_res[i][5]) == 1:
                                        fina_res.append(9)
                                    elif int(all_res[i][5]) == 3:
                                        fina_res.append(0)
                                    elif int(all_res[i][5]) == 4:
                                        fina_res.append(8)
                                    elif int(all_res[i][5]) == 5:
                                        fina_res.append(3)
                                    elif int(all_res[i][5]) == 6:
                                        fina_res.append(4)
                                    elif int(all_res[i][5]) == 7:
                                        fina_res.append(2)
                                    elif int(all_res[i][5]) == 8:
                                        fina_res.append(7)
                                    elif int(all_res[i][5]) == 9:
                                        fina_res.append(5)
                                    elif int(all_res[i][5]) == 0:
                                        fina_res.append(6)

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型   号：FLUKE 115C' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型   号：FLUKE 115C' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(fina_res) != 0:
                                        fina_res.reverse()
                                        with open('result.txt', 'a') as file:
                                            # >>>>>>>判断小数点位置>>>>>>>
                                            num_res = ''.join(map(str, fina_res))
                                            # print(result)
                                            # print(float(num_res))
                                            if point_flag == 1:
                                                num_res = float(num_res) / 1000
                                            elif point_flag == 2:
                                                num_res = float(num_res) / 100
                                            elif point_flag == 3:
                                                num_res = float(num_res) / 10
                                            num_res = str(num_res)

                                            # <<<<<<<判断小数点位置<<<<<<<
                                            file.write(num_res + '\n')    # roi_numshow_res[numshow_index][0]
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write(num_res + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                # mV 区域
                                mV_115c = AxisProportion(2.9, 3.16, 1.44, 1.55)

                                draw.rectangle((axis_x1 + mV_115c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + mV_115c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + mV_115c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + mV_115c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + mV_115c.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + mV_115c.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + mV_115c.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + mV_115c.axis_right * (axis_x2 - axis_x1))]
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + 2 * (axis_y2 - axis_y1)):int(axis_y1 + 2.6 * (axis_y2 - axis_y1)),
                                                       int(axis_x2 - 0.03 * (axis_x2 - axis_x1)):int(axis_x2 + 0.35 * (axis_x2 - axis_x1))]

                                # roi_mV 高宽
                                roi_mV_height, roi_mV_width = roi_mV_arr.shape[:2]

                                # 500外框
                                new_roi_mV_height = roi_mV_height + 1000
                                new_roi_mV_width = roi_mV_width + 1000
                                new_roi_mV_arr = np.zeros((new_roi_mV_height, new_roi_mV_width, 3), np.uint8)
                                new_roi_mV_arr[500:new_roi_mV_height - 500, 500:new_roi_mV_width - 500] = roi_mV_arr

                                roi_mV_boxes, roi_mVshow_res, _ = self.__call__(new_roi_mV_arr, cls)
                                mVshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                    if len(roi_mVshow_res) != 0:
                                        for mVshow_index in range(0, len(roi_mVshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mVshow_res[mVshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mVshow_res[mVshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # AC、DC 区域
                                ad_115c = AxisProportion(2.9, 3.16, 1.95, 1.96)

                                draw.rectangle((axis_x1 + ad_115c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_115c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_115c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_115c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AD_arr = 255 * img[int(axis_y1 + ad_115c.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_115c.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_115c.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_115c.axis_right * (axis_x2 - axis_x1))]

                                # roi_AD高宽
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]

                                # 500外框
                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                # A/M 区域
                                am_115c = AxisProportion(-0.85, 0.78, 2.96, 2.99)
                                draw.rectangle((axis_x1 + am_115c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + am_115c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_115c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_115c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y1 + am_115c.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + am_115c.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_115c.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + am_115c.axis_right * (axis_x2 - axis_x1))]

                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y2 + 2.9 * (axis_y2 - axis_y1)):int(axis_y2 + 3.4 * (axis_y2 - axis_y1)),
                                                       int(axis_x1 - 0.15 * (axis_x2 - axis_x1)):int(axis_x2 - 0.3 * (axis_x2 - axis_x1))]

                                # roi_AM高宽
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]
                                # 500外框
                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # 177c
                            elif 20 <= class_index <= 24:
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                # 屏幕区域
                                screen_177c = AxisProportion(-0.60, 0.10, 0.15, 0.88)

                                draw.rectangle((axis_x1 + screen_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_177c.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.13, -1.07, 0.6, 0.62),
                                    AxisProportion(0.13, -0.81, 0.6, 0.62),
                                    AxisProportion(0.40, -0.53, 0.6, 0.62)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2,
                                                                           axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                                # 示数区域
                                num_177c = AxisProportion(- 0.5, -0.3, 0.3, 0.63)
                                draw.rectangle((axis_x1 + num_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_177c.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)  # 11.1
                                fina_res = []
                                all_res = detect.detect_number()
                                for i in range(all_res.__len__()):
                                    if int(all_res[i][5]) == 2:
                                        fina_res.append(1)
                                    elif int(all_res[i][5]) == 1:
                                        fina_res.append(9)
                                    elif int(all_res[i][5]) == 3:
                                        fina_res.append(0)
                                    elif int(all_res[i][5]) == 4:
                                        fina_res.append(8)
                                    elif int(all_res[i][5]) == 5:
                                        fina_res.append(3)
                                    elif int(all_res[i][5]) == 6:
                                        fina_res.append(4)
                                    elif int(all_res[i][5]) == 7:
                                        fina_res.append(2)
                                    elif int(all_res[i][5]) == 8:
                                        fina_res.append(7)
                                    elif int(all_res[i][5]) == 9:
                                        fina_res.append(5)
                                    elif int(all_res[i][5]) == 0:
                                        fina_res.append(6)

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型   号：FLUKE 177C ' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型   号：FLUKE 15B+' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(fina_res) != 0:
                                        fina_res.reverse()
                                        with open('result.txt', 'a') as file:
                                            # >>>>>>>判断小数点位置>>>>>>>
                                            num_res = ''.join(map(str, fina_res))
                                            # print(result)
                                            # print(float(num_res))
                                            if point_flag == 1:
                                                num_res = float(num_res) / 1000
                                            elif point_flag == 2:
                                                num_res = float(num_res) / 100
                                            elif point_flag == 3:
                                                num_res = float(num_res) / 10
                                            num_res = str(num_res)
                                            point_flag = 0  #
                                            # <<<<<<<判断小数点位置<<<<<<<
                                            file.write(num_res + '\n')    # roi_numshow_res[numshow_index][0]
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write(num_res + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                # omega
                                Momega_177c = AxisProportion(0.7, 0.04, 0.48, 0.53)

                                draw.rectangle((axis_x1 + Momega_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + Momega_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + Momega_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + Momega_177c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_Momega_arr = 255 * img[int(axis_y1 + Momega_177c.axis_up * (axis_x2 - axis_x1)):
                                                           int(axis_y2 + Momega_177c.axis_down * (axis_x2 - axis_x1)),
                                                       int(axis_x1 + Momega_177c.axis_left * (axis_x2 - axis_x1)):
                                                       int(axis_x2 + Momega_177c.axis_right * (axis_x2 - axis_x1))]

                                # roi_Momega高宽
                                roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]

                                new_roi_Momega_height = roi_Momega_height + 1000
                                new_roi_Momega_width = roi_Momega_width + 1000
                                new_roi_Momega_arr = np.zeros((new_roi_Momega_height, new_roi_Momega_width, 3),
                                                              np.uint8)

                                new_roi_Momega_arr[500:new_roi_Momega_height - 500,
                                500:new_roi_Momega_width - 500] = roi_Momega_arr

                                roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                Momegashow_index = 0

                                # detect.detect_omega()

                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                    if len(roi_Momegashow_res) != 0:
                                        for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_Momegashow_res[Momegashow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_Momegashow_res[Momegashow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧米伽：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧米伽：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> nf >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  nf  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  nf  ：' + ' ')
                                # <<<<<<<<<<<<<<<< nf <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                #######################################################################################################################################################
                                # mV区域
                                mV_177c = AxisProportion(0.72, 0.02, 0.3, 0.36)

                                draw.rectangle((axis_x1 + mV_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + mV_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + mV_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + mV_177c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + mV_177c.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + mV_177c.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + mV_177c.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + mV_177c.axis_right * (axis_x2 - axis_x1))]

                                # roi_mV高宽
                                roi_mV_height, roi_mV_width = roi_mV_arr.shape[:2]
                                # 500外框
                                new_roi_mV_height = roi_mV_height + 1000
                                new_roi_mV_width = roi_mV_width + 1000
                                new_roi_mV_arr = np.zeros((new_roi_mV_height, new_roi_mV_width, 3),
                                                          np.uint8)

                                new_roi_mV_arr[500:new_roi_mV_height - 500,
                                500:new_roi_mV_width - 500] = roi_mV_arr

                                roi_mV_boxes, roi_mVshow_res, _ = self.__call__(new_roi_mV_arr, cls)
                                mVshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                    if len(roi_mVshow_res) != 0:
                                        for mVshow_index in range(0, len(roi_mVshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mVshow_res[mVshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mVshow_res[mVshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # AC、DC 区域
                                ad_177c = AxisProportion(0.73, -0.01, 0.41, 0.43)

                                draw.rectangle((axis_x1 + ad_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_177c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AD_arr = 255 * img[int(axis_y1 + ad_177c.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_177c.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_177c.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_177c.axis_right * (axis_x2 - axis_x1))]

                                # roi_AD高宽
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]
                                # 500外框
                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # μmA 区域
                                miu_177c = AxisProportion(0.81, 0.05, 0.93, 1.0)
                                draw.rectangle((axis_x1 + miu_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + miu_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + miu_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + miu_177c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_miu_arr = 255 * img[int(axis_y1 + miu_177c.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + miu_177c.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x1 + miu_177c.axis_left * (axis_x2 - axis_x1)):
                                                    int(axis_x2 + miu_177c.axis_right * (axis_x2 - axis_x1))]

                                # roi_miu高宽
                                roi_miu_height, roi_miu_width = roi_miu_arr.shape[:2]
                                # 500外框
                                new_roi_miu_height = roi_miu_height + 1000
                                new_roi_miu_width = roi_miu_width + 1000
                                new_roi_miu_arr = np.zeros((new_roi_miu_height, new_roi_miu_width, 3), np.uint8)

                                new_roi_miu_arr[500:new_roi_miu_height - 500, 500:new_roi_miu_width - 500] = roi_miu_arr

                                roi_miu_boxes, roi_miushow_res, _ = self.__call__(new_roi_miu_arr, cls)
                                miushow_index = 0

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                    # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<
                                    if len(roi_miushow_res) != 0:
                                        for miushow_index in range(0, len(roi_miushow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_miushow_res[miushow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_miushow_res[miushow_index][0] + '\n')

                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # A/M 区域
                                am_177c = AxisProportion(-0.22, -0.4, 0.69, 0.72)

                                draw.rectangle((axis_x1 + am_177c.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + am_177c.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_177c.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_177c.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y1 + am_177c.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + am_177c.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_177c.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + am_177c.axis_right * (axis_x2 - axis_x1))]

                                # roi_AM高宽
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]

                                # 500外框
                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                ######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # 312clamp meter
                            elif 25 <= class_index <= 29:
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                # 屏幕区域
                                screen_312 = AxisProportion(-0.75, -0.05, -1.15, -0.28)

                                draw.rectangle((axis_x1 + screen_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_312.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.35, -1.25, -0.54, -0.51),
                                    AxisProportion(-0.02, -0.92, -0.54, -0.51),
                                    AxisProportion(0.3, -0.6, -0.54, -0.51)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2,
                                                                           axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<
                                # 示数区域
                                num_312 = AxisProportion(- 0.58, -0.13, 0.48, 1.03)
                                draw.rectangle((axis_x1 + num_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_312.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)  # 11.1

                                # 裁剪ROI图像
                                roi_num_arr = 255 * img[int(axis_y1 + num_312.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + num_312.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x1 + num_312.axis_left * (axis_x2 - axis_x1)):
                                                    int(axis_x2 + num_312.axis_right * (axis_x2 - axis_x1))]

                                # roi_num高宽
                                roi_num_height, roi_num_width = roi_num_arr.shape[:2]

                                # 给ROi一个宽度为500的外框
                                new_roi_num_height = roi_num_height + 1000
                                new_roi_num_width = roi_num_width + 1000
                                new_roi_num_arr = np.zeros((new_roi_num_height, new_roi_num_width, 3), np.uint8)
                                new_roi_num_arr[500:new_roi_num_height - 500, 500:new_roi_num_width - 500] = roi_num_arr

                                roi_num_boxes, roi_numshow_res, _ = self.__call__(new_roi_num_arr, cls)
                                numshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型   号：FLUKE 312+' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型   号：FLUKE 312+' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(roi_numshow_res) != 0:
                                        for numshow_index in range(0, len(roi_numshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_numshow_res[numshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_numshow_res[numshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                ######################################################################################################################################################
                                # MΩ 区域
                                Momega_312 = AxisProportion(0.6, -0.04, 0.35, 0.43)
                                draw.rectangle((axis_x1 + Momega_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + Momega_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + Momega_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + Momega_312.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_Momega_arr = 255 * img[int(axis_y1 + Momega_312.axis_up * (axis_x2 - axis_x1)):
                                                           int(axis_y2 + Momega_312.axis_down * (axis_x2 - axis_x1)),
                                                       int(axis_x1 + Momega_312.axis_left * (axis_x2 - axis_x1)):
                                                       int(axis_x2 + Momega_312.axis_right * (axis_x2 - axis_x1))]

                                # roi_Momega高宽
                                roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]

                                new_roi_Momega_height = roi_Momega_height + 1000
                                new_roi_Momega_width = roi_Momega_width + 1000
                                new_roi_Momega_arr = np.zeros((new_roi_Momega_height, new_roi_Momega_width, 3),
                                                              np.uint8)

                                new_roi_Momega_arr[500:new_roi_Momega_height - 500,
                                500:new_roi_Momega_width - 500] = roi_Momega_arr

                                roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                Momegashow_index = 0

                                # detect.detect_omega()

                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                    if len(roi_Momegashow_res) != 0:
                                        for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_Momegashow_res[Momegashow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_Momegashow_res[Momegashow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧米伽：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧米伽：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> nf >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  nf  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  nf  ：' + ' ')
                                # <<<<<<<<<<<<<<<< nf <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                #######################################################################################################################################################
                                # mV区域
                                mV_312 = AxisProportion(0.75, -0.1, -0.95, -0.9)

                                draw.rectangle((axis_x1 + mV_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + mV_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + mV_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + mV_312.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + mV_312.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + mV_312.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + mV_312.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + mV_312.axis_right * (axis_x2 - axis_x1))]

                                # roi_mV高宽
                                roi_mV_height, roi_mV_width = roi_mV_arr.shape[:2]
                                # 500外框
                                new_roi_mV_height = roi_mV_height + 1000
                                new_roi_mV_width = roi_mV_width + 1000
                                new_roi_mV_arr = np.zeros((new_roi_mV_height, new_roi_mV_width, 3),
                                                          np.uint8)

                                new_roi_mV_arr[500:new_roi_mV_height - 500,
                                500:new_roi_mV_width - 500] = roi_mV_arr

                                roi_mV_boxes, roi_mVshow_res, _ = self.__call__(new_roi_mV_arr, cls)
                                mVshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                    if len(roi_mVshow_res) != 0:
                                        for mVshow_index in range(0, len(roi_mVshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mVshow_res[mVshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mVshow_res[mVshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # AC、DC 区域
                                ad_312 = AxisProportion(0.75, -0.1, -0.65, -0.5)

                                draw.rectangle((axis_x1 + ad_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_312.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AD_arr = 255 * img[int(axis_y1 + ad_312.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_312.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_312.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_312.axis_right * (axis_x2 - axis_x1))]

                                # roi_AD高宽
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]
                                # 500外框
                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # μmA 区域
                                miu_312 = AxisProportion(0.81, 0.05, 0.93, 1.0)
                                draw.rectangle((axis_x1 + miu_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + miu_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + miu_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + miu_312.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_miu_arr = 255 * img[int(axis_y1 + miu_312.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + miu_312.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x1 + miu_312.axis_left * (axis_x2 - axis_x1)):
                                                    int(axis_x2 + miu_312.axis_right * (axis_x2 - axis_x1))]

                                # roi_miu高宽
                                roi_miu_height, roi_miu_width = roi_miu_arr.shape[:2]
                                # 500外框
                                new_roi_miu_height = roi_miu_height + 1000
                                new_roi_miu_width = roi_miu_width + 1000
                                new_roi_miu_arr = np.zeros((new_roi_miu_height, new_roi_miu_width, 3), np.uint8)

                                new_roi_miu_arr[500:new_roi_miu_height - 500, 500:new_roi_miu_width - 500] = roi_miu_arr

                                roi_miu_boxes, roi_miushow_res, _ = self.__call__(new_roi_miu_arr, cls)
                                miushow_index = 0

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                    # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<
                                    if len(roi_miushow_res) != 0:
                                        for miushow_index in range(0, len(roi_miushow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_miushow_res[miushow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_miushow_res[miushow_index][0] + '\n')

                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # A/M 区域
                                am_312 = AxisProportion(0.65, -0.1, -0.55, -0.5)

                                draw.rectangle((axis_x1 + am_312.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + am_312.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_312.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_312.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y1 + am_312.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + am_312.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_312.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + am_312.axis_right * (axis_x2 - axis_x1))]

                                # roi_AM高宽
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]

                                # 500外框
                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                ######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # kkyor
                            elif 30 <= class_index <= 34:
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                # 屏幕区域
                                screen_kkyor = AxisProportion(-0.46, 0.18, 0.21, 0.63)

                                draw.rectangle((axis_x1 + screen_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_kkyor.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.14, -1.06, 0.64, 0.56),
                                    AxisProportion(0.18, -0.75, 0.64, 0.56),
                                    AxisProportion(0.46, -0.47, 0.64, 0.56)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2,
                                                                           axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                                # 示数区域
                                num_kkyor = AxisProportion(- 0.58, -0.13, 0.48, 1.03)
                                draw.rectangle((axis_x1 + num_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_kkyor.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)  # 11.1

                                # 裁剪ROI图像
                                roi_num_arr = 255 * img[int(axis_y1 + num_kkyor.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + num_kkyor.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x1 + num_kkyor.axis_left * (axis_x2 - axis_x1)):
                                                    int(axis_x2 + num_kkyor.axis_right * (axis_x2 - axis_x1))]

                                # roi_num高宽
                                roi_num_height, roi_num_width = roi_num_arr.shape[:2]

                                # 给ROi一个宽度为500的外框
                                new_roi_num_height = roi_num_height + 1000
                                new_roi_num_width = roi_num_width + 1000
                                new_roi_num_arr = np.zeros((new_roi_num_height, new_roi_num_width, 3), np.uint8)
                                new_roi_num_arr[500:new_roi_num_height - 500, 500:new_roi_num_width - 500] = roi_num_arr

                                roi_num_boxes, roi_numshow_res, _ = self.__call__(new_roi_num_arr, cls)
                                numshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型   号：FLUKE kkyor+' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型   号：FLUKE kkyor+' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(roi_numshow_res) != 0:
                                        for numshow_index in range(0, len(roi_numshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_numshow_res[numshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_numshow_res[numshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                ######################################################################################################################################################
                                # MΩ 区域
                                Momega_kkyor = AxisProportion(0.6, -0.04, 0.35, 0.43)
                                draw.rectangle((axis_x1 + Momega_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + Momega_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + Momega_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + Momega_kkyor.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_Momega_arr = 255 * img[int(axis_y1 + Momega_kkyor.axis_up * (axis_x2 - axis_x1)):
                                                           int(axis_y2 + Momega_kkyor.axis_down * (axis_x2 - axis_x1)),
                                                       int(axis_x1 + Momega_kkyor.axis_left * (axis_x2 - axis_x1)):
                                                       int(axis_x2 + Momega_kkyor.axis_right * (axis_x2 - axis_x1))]

                                # roi_Momega高宽
                                roi_Momega_height, roi_Momega_width = roi_Momega_arr.shape[:2]

                                new_roi_Momega_height = roi_Momega_height + 1000
                                new_roi_Momega_width = roi_Momega_width + 1000
                                new_roi_Momega_arr = np.zeros((new_roi_Momega_height, new_roi_Momega_width, 3),
                                                              np.uint8)

                                new_roi_Momega_arr[500:new_roi_Momega_height - 500,
                                500:new_roi_Momega_width - 500] = roi_Momega_arr

                                roi_Momega_boxes, roi_Momegashow_res, _ = self.__call__(new_roi_Momega_arr, cls)
                                Momegashow_index = 0

                                # detect.detect_omega()

                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                    if len(roi_Momegashow_res) != 0:
                                        for Momegashow_index in range(0, len(roi_Momegashow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_Momegashow_res[Momegashow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_Momegashow_res[Momegashow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧米伽：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧米伽：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> nf >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  nf  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  nf  ：' + ' ')
                                # <<<<<<<<<<<<<<<< nf <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                #######################################################################################################################################################
                                # mV区域
                                mV_kkyor = AxisProportion(0.87, 0.06, 0.64, 0.70)
                                draw.rectangle((axis_x1 + mV_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + mV_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + mV_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + mV_kkyor.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + mV_kkyor.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + mV_kkyor.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + mV_kkyor.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + mV_kkyor.axis_right * (axis_x2 - axis_x1))]

                                # roi_mV高宽
                                roi_mV_height, roi_mV_width = roi_mV_arr.shape[:2]
                                # 500外框
                                new_roi_mV_height = roi_mV_height + 1000
                                new_roi_mV_width = roi_mV_width + 1000
                                new_roi_mV_arr = np.zeros((new_roi_mV_height, new_roi_mV_width, 3),
                                                          np.uint8)

                                new_roi_mV_arr[500:new_roi_mV_height - 500,
                                500:new_roi_mV_width - 500] = roi_mV_arr

                                roi_mV_boxes, roi_mVshow_res, _ = self.__call__(new_roi_mV_arr, cls)
                                mVshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                    if len(roi_mVshow_res) != 0:
                                        for mVshow_index in range(0, len(roi_mVshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mVshow_res[mVshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mVshow_res[mVshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # AC、DC 区域
                                ad_kkyor = AxisProportion(-0.46, -1.26, 0.53, 0.53)
                                draw.rectangle((axis_x1 + ad_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_kkyor.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AD_arr = 255 * img[int(axis_y1 + ad_kkyor.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_kkyor.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_kkyor.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_kkyor.axis_right * (axis_x2 - axis_x1))]

                                # roi_AD高宽
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]
                                # 500外框
                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # μmA 区域
                                miu_kkyor = AxisProportion(0.77, 0.05, 0.3, 0.33)
                                draw.rectangle((axis_x1 + miu_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + miu_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + miu_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + miu_kkyor.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_miu_arr = 255 * img[int(axis_y1 + miu_kkyor.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + miu_kkyor.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x1 + miu_kkyor.axis_left * (axis_x2 - axis_x1)):
                                                    int(axis_x2 + miu_kkyor.axis_right * (axis_x2 - axis_x1))]

                                # roi_miu高宽
                                roi_miu_height, roi_miu_width = roi_miu_arr.shape[:2]
                                # 500外框
                                new_roi_miu_height = roi_miu_height + 1000
                                new_roi_miu_width = roi_miu_width + 1000
                                new_roi_miu_arr = np.zeros((new_roi_miu_height, new_roi_miu_width, 3), np.uint8)

                                new_roi_miu_arr[500:new_roi_miu_height - 500, 500:new_roi_miu_width - 500] = roi_miu_arr

                                roi_miu_boxes, roi_miushow_res, _ = self.__call__(new_roi_miu_arr, cls)
                                miushow_index = 0

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                    # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<
                                    if len(roi_miushow_res) != 0:
                                        for miushow_index in range(0, len(roi_miushow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_miushow_res[miushow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_miushow_res[miushow_index][0] + '\n')

                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # A/M 区域
                                am_kkyor = AxisProportion(-0.12, -0.46, 1.08, 1.14)
                                draw.rectangle((axis_x1 + am_kkyor.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + am_kkyor.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_kkyor.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_kkyor.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y1 + am_kkyor.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + am_kkyor.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_kkyor.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + am_kkyor.axis_right * (axis_x2 - axis_x1))]

                                # roi_AM高宽
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]

                                # 500外框
                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][
                                                               0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                ######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # 数字兆欧表 DIGITAL MEGOHM
                            elif 35 <= class_index <= 39:
                                with open('result.txt', 'a') as file:
                                    file.write('型   号：' + 'BY2671 数字兆欧表')
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('型   号：' + 'BY2671 数字兆欧表')
                                    file_log.write('\n')
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                ##########################################################################
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(0.19, 0.24, 0.557, 0.563),
                                    AxisProportion(0.47, 0.52, 0.557, 0.563),
                                    AxisProportion(0.74, 0.79, 0.557, 0.563)
                                ]
                                point_position = MarkPoint(point_proportion=0.08)
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2, axis_y2, points)
                                # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<
                                #######################################################################################################################################################
                                # 屏幕区域/示数区域
                                num_BY2671 = AxisProportion(-0.13, 0.12, 0.20, 0.63)
                                draw.rectangle((axis_x1 + num_BY2671.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_BY2671.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_BY2671.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_BY2671.axis_down * (axis_x2 - axis_x1)), outline='red',
                                               width=3)
                                # 裁剪roi图像
                                roi_SCR_arr = 255 * img[int(axis_y1 + num_BY2671.axis_up * (axis_x2 - axis_x1)):
                                                        int(axis_y2 + num_BY2671.axis_down * (axis_x2 - axis_x1)),
                                                    int(axis_x1 + num_BY2671.axis_left * (axis_x2 - axis_x1)):
                                                    int(axis_x2 + num_BY2671.axis_right * (axis_x2 - axis_x1))]
                                roi_SCR_height, roi_SCR_width = roi_SCR_arr.shape[:2]

                                # 500外框
                                new_roi_SCR_height = roi_SCR_height + 1000
                                new_roi_SCR_width = roi_SCR_width + 1000
                                new_roi_SCR_arr = np.zeros((new_roi_SCR_height, new_roi_SCR_width, 3), np.uint8)

                                new_roi_SCR_arr[500:new_roi_SCR_height - 500, 500:new_roi_SCR_width - 500] = roi_SCR_arr

                                roi_SCR_boxes, roi_numshow_res, _ = self.__call__(new_roi_SCR_arr, cls)
                                SCRshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('示  数：' + ' ')
                                    if len(roi_numshow_res) != 0:
                                        for numshow_index in range(0, len(roi_numshow_res[0]) - 1):
                                            # >>>>>>>判断小数点位置>>>>>>>
                                            num_res = roi_numshow_res[numshow_index][0]
                                            num_res = num_res.replace('.', '')

                                            # print(float(num_res))
                                            if point_flag == 1:
                                                num_res = float(num_res) / 1000
                                            elif point_flag == 2:
                                                num_res = float(num_res) / 100
                                            elif point_flag == 3:
                                                num_res = float(num_res) / 10
                                            num_res = str(num_res)
                                            # <<<<<<<判断小数点位置<<<<<<<
                                            with open('result.txt', 'a') as file:
                                                if roi_numshow_res[numshow_index][0] == '!' or \
                                                        roi_numshow_res[numshow_index][0] == '！':
                                                    file.write('1' + '\n')
                                                else:
                                                    file.write(num_res + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(num_res + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                '''
                                ##########################################################
                                箱式数字兆欧表--灯（开始）
                                ##########################################################
                                '''
                                # light on/off
                                light_on_figure = AxisProportion(0.45, 0.65, 0.95, 1.15)
                                # point3_17b = Axis_proportion(0.47, -0.43, 0.88, 0.95)
                                draw.rectangle((axis_x1 + light_on_figure.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + light_on_figure.axis_up * (axis_x2 - axis_x1),
                                                axis_x1 + light_on_figure.axis_right * (axis_x2 - axis_x1),
                                                axis_y1 + light_on_figure.axis_down * (axis_x2 - axis_x1)),
                                               outline='green', width=5)

                                # light 500v
                                light_500_figure = AxisProportion(-0.05, 0.15, 1.25, 1.45)
                                # point3_17b = Axis_proportion(0.47, -0.43, 0.88, 0.95)
                                draw.rectangle((axis_x1 + light_500_figure.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + light_500_figure.axis_up * (axis_x2 - axis_x1),
                                                axis_x1 + light_500_figure.axis_right * (axis_x2 - axis_x1),
                                                axis_y1 + light_500_figure.axis_down * (axis_x2 - axis_x1)),
                                               outline='green', width=5)

                                # light 1000v
                                light_1000_figure = AxisProportion(0.15, 0.35, 1.65, 1.85)
                                draw.rectangle((axis_x1 + light_1000_figure.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + light_1000_figure.axis_up * (axis_x2 - axis_x1),
                                                axis_x1 + light_1000_figure.axis_right * (axis_x2 - axis_x1),
                                                axis_y1 + light_1000_figure.axis_down * (axis_x2 - axis_x1)),
                                               outline='green', width=5)

                                # light 2000v
                                light_2000_figure = AxisProportion(0.85, 1.05, 1.65, 1.85)
                                draw.rectangle((axis_x1 + light_2000_figure.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + light_2000_figure.axis_up * (axis_x2 - axis_x1),
                                                axis_x1 + light_2000_figure.axis_right * (axis_x2 - axis_x1),
                                                axis_y1 + light_2000_figure.axis_down * (axis_x2 - axis_x1)),
                                               outline='green', width=5)

                                # light 2500v
                                light_2500_figure = AxisProportion(1.05, 1.25, 1.25, 1.45)
                                draw.rectangle((axis_x1 + light_2500_figure.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + light_2500_figure.axis_up * (axis_x2 - axis_x1),
                                                axis_x1 + light_2500_figure.axis_right * (axis_x2 - axis_x1),
                                                axis_y1 + light_2500_figure.axis_down * (axis_x2 - axis_x1)),
                                               outline='green', width=5)

                                '''
                                ##########################################################
                                箱式数字兆欧表--灯（结束）
                                ##########################################################
                                '''

                                # >>>>>>>>>>>>>>>> 欧姆 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧姆 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧米伽：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧米伽：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> nf >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  nf  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  nf  ：' + ' ')
                                # <<<<<<<<<<<<<<<< nf <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> mV >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                # <<<<<<<<<<<<<<<< mV <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> A/D >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                # <<<<<<<<<<<<<<<< A/D <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> A/M >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                # <<<<<<<<<<<<<<<< A/M <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                img_pil.show()

                            # UNI 400counts
                            elif 40 <= class_index <= 44:
                                # 型号
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)

                                # 屏幕区域
                                screen_uni = AxisProportion(-1.6, 0.1, -2, -0.3)
                                draw.rectangle((axis_x1 + screen_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + screen_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + screen_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + screen_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                                points = [
                                    AxisProportion(-0.14, -1.06, 0.64, 0.56),
                                    AxisProportion(0.18, -0.75, 0.64, 0.56),
                                    AxisProportion(0.46, -0.47, 0.64, 0.56)
                                ]
                                point_position = MarkPoint()
                                point_flag = point_position.process_points(draw, img, axis_x1, axis_y1, axis_x2,
                                                                           axis_y2, points)
                                #######################################################################################################################################################
                                # 示数区域
                                num_uni = AxisProportion(-1.2, 0.1, -1.7, -0.6)
                                draw.rectangle((axis_x1 + num_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + num_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + num_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + num_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_num_arr = 255 * img[int(axis_y1 + num_uni.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + num_uni.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + num_uni.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + num_uni.axis_right * (axis_x2 - axis_x1))]

                                # roi_num的高宽
                                roi_num_height, roi_num_width = roi_num_arr.shape[:2]

                                # 500外框
                                new_roi_num_height = roi_num_height + 1000
                                new_roi_num_width = roi_num_width + 1000
                                new_roi_num_arr = np.zeros((new_roi_num_height, new_roi_num_width, 3), np.uint8)
                                new_roi_num_arr[500:new_roi_num_height - 500, 500:new_roi_num_width - 500] = roi_num_arr

                                # cv2.imwrite("new_roi_num_arr.png", new_roi_num_arr)
                                # cv2.imwrite("roi_num_arr.png", roi_num_arr)

                                roi_num_boxes, roi_numshow_res, _ = self.__call__(new_roi_num_arr, cls)
                                numshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('\n' + '型    号：UNI：' + '\n')
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n' + '型    号：UNI：' + '\n')
                                    file_log.write('示  数：' + ' ')
                                    if len(roi_numshow_res) != 0:
                                        for numshow_index in range(0, len(roi_numshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_numshow_res[numshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_numshow_res[numshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # mV 区域
                                mV_uni = AxisProportion(-0.1, -0.55, -2, -1.85)
                                draw.rectangle((axis_x1 + mV_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + mV_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + mV_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + mV_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_mV_arr = 255 * img[int(axis_y1 + mV_uni.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + mV_uni.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + mV_uni.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + mV_uni.axis_right * (axis_x2 - axis_x1))]

                                # roi_mV的高宽
                                roi_mV_height, roi_mV_width = roi_mV_arr.shape[:2]

                                # 500外框
                                new_roi_mV_height = roi_mV_height + 1000
                                new_roi_mV_width = roi_mV_width + 1000
                                new_roi_mV_arr = np.zeros((new_roi_mV_height, new_roi_mV_width, 3), np.uint8)

                                new_roi_mV_arr[500:new_roi_mV_height - 500, 500:new_roi_mV_width - 500] = roi_mV_arr

                                roi_mV_boxes, roi_mVshow_res, _ = self.__call__(new_roi_mV_arr, cls)
                                mVshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write('  V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  V  ：' + ' ')
                                    if len(roi_mVshow_res) != 0:
                                        for mVshow_index in range(0, len(roi_mVshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mVshow_res[mVshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mVshow_res[mVshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # AC、DC 区域
                                ad_uni = AxisProportion(-1.6, -2.1, -1.3, -0.95)
                                draw.rectangle((axis_x1 + ad_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + ad_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + ad_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + ad_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AD_arr = 255 * img[int(axis_y1 + ad_uni.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + ad_uni.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + ad_uni.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + ad_uni.axis_right * (axis_x2 - axis_x1))]

                                # roi_AD的高宽
                                roi_AD_height, roi_AD_width = roi_AD_arr.shape[:2]
                                # 500外框
                                new_roi_AD_height = roi_AD_height + 1000
                                new_roi_AD_width = roi_AD_width + 1000
                                new_roi_AD_arr = np.zeros((new_roi_AD_height, new_roi_AD_width, 3), np.uint8)

                                new_roi_AD_arr[500:new_roi_AD_height - 500, 500:new_roi_AD_width - 500] = roi_AD_arr

                                roi_AD_boxes, roi_ADshow_res, _ = self.__call__(new_roi_AD_arr, cls)
                                ADshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                    if len(roi_ADshow_res) != 0:
                                        for ADshow_index in range(0, len(roi_ADshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_ADshow_res[ADshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_ADshow_res[ADshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                Momega_uni = AxisProportion(-0.85, -1.5, -2, -1.85)
                                draw.rectangle((axis_x1 + Momega_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + Momega_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + Momega_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + Momega_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # hz 区域
                                hz_uni = AxisProportion(-0.6, -1.3, -2, -1.85)
                                draw.rectangle((axis_x1 + hz_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + hz_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + hz_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + hz_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_hz_arr = 255 * img[int(axis_y1 + hz_uni.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + hz_uni.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + hz_uni.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + hz_uni.axis_right * (axis_x2 - axis_x1))]

                                # roi_hz高宽
                                roi_hz_height, roi_hz_width = roi_hz_arr.shape[:2]

                                new_roi_hz_height = roi_hz_height + 1000
                                new_roi_hz_width = roi_hz_width + 1000
                                new_roi_hz_arr = np.zeros((new_roi_hz_height, new_roi_hz_width, 3), np.uint8)

                                new_roi_hz_arr[500:new_roi_hz_height - 500, 500:new_roi_hz_width - 500] = roi_hz_arr

                                roi_hz_boxes, roi_hzshow_res, _ = self.__call__(new_roi_hz_arr, cls)
                                hzshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' HZ  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' HZ  ：' + ' ')
                                    if len(roi_hzshow_res) != 0:
                                        for hzshow_index in range(0, len(roi_hzshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_hzshow_res[hzshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_hzshow_res[hzshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # A/M 区域
                                am_uni = AxisProportion(-1.6, -1.2, -0.43, -0.3)
                                draw.rectangle((axis_x1 + am_uni.axis_left * (axis_x2 - axis_x1),
                                                axis_y1 + am_uni.axis_up * (axis_x2 - axis_x1),
                                                axis_x2 + am_uni.axis_right * (axis_x2 - axis_x1),
                                                axis_y2 + am_uni.axis_down * (axis_x2 - axis_x1)), outline='blue',
                                               width=3)
                                # 裁剪ROI图像
                                roi_AM_arr = 255 * img[int(axis_y1 + am_uni.axis_up * (axis_x2 - axis_x1)):
                                                       int(axis_y2 + am_uni.axis_down * (axis_x2 - axis_x1)),
                                                   int(axis_x1 + am_uni.axis_left * (axis_x2 - axis_x1)):
                                                   int(axis_x2 + am_uni.axis_right * (axis_x2 - axis_x1))]

                                # roi_AM高宽
                                roi_AM_height, roi_AM_width = roi_AM_arr.shape[:2]

                                new_roi_AM_height = roi_AM_height + 1000
                                new_roi_AM_width = roi_AM_width + 1000
                                new_roi_AM_arr = np.zeros((new_roi_AM_height, new_roi_AM_width, 3), np.uint8)

                                new_roi_AM_arr[500:new_roi_AM_height - 500, 500:new_roi_AM_width - 500] = roi_AM_arr

                                roi_AM_boxes, roi_AMshow_res, _ = self.__call__(new_roi_AM_arr, cls)
                                AMshow_index = 0

                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                    if len(roi_AMshow_res) != 0:
                                        for AMshow_index in range(0, len(roi_AMshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_AMshow_res[AMshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_AMshow_res[AMshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')

                                #######################################################################################################################################################
                                # 结果显示
                                img_pil.show()

                            # VICTOR
                            elif 45 <= class_index <= 49:
                                with open('result.txt', 'a') as file:
                                    file.write('型   号：' + 'VICTOR 6800')
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('型   号：' + 'VICTOR 6800')
                                    file_log.write('\n')
                                draw.rectangle((axis_x1, axis_y1, axis_x2, axis_y2), outline='red', width=3)
                                #######################################################################################################################################################
                                # 屏幕区域
                                # draw.rectangle((axis_x1 + 0.13 * (axis_x2 - axis_x1),
                                #                 axis_y1 + 2.5 * (axis_x2 - axis_x1),
                                #                 axis_x2 + 0.68 * (axis_x2 - axis_x1),
                                #                 axis_y2 + 3.1 * (axis_x2 - axis_x1)), outline='red', width=3)
                                victor_screen_x1, victor_screen_y1,victor_screen_x2,victor_screen_y2 = detect.detect_qianxing_screen()
                                draw.rectangle((victor_screen_x1,
                                                    victor_screen_y1,
                                                    victor_screen_x2,
                                                    victor_screen_y2), outline='red', width=3)
                                # 保存

                                # img_pil_sceen.show()
                                # draw.rectangle((victor_screen_x1 - 480,
                                #                 victor_screen_y1 + 550,
                                #                 victor_screen_x2 - 480,
                                #                 victor_screen_y2 + 550), outline='red', width=3)
                                # >>>>>>>>>>>>>>> 小数点 >>>>>>>>>>>>>
                                point_proportion = 0.5  # 像素占比
                                point_flag = 0  # 判断小数点在哪个位置，0表示没有小数点

                                # 打开二值化之后的图片
                                path_binary = "C:\\Users\\4090\\Desktop\\screen_crop\\screen_crop_binary.jpg"
                                img_binary = cv2.imread(path_binary)
                                img_binary = img_binary[:, :, [2, 1, 0]]
                                img_binary = (img_binary - img_binary.min()) / (img_binary.max() - img_binary.min())

                                image_pil = Image.open(path_binary)
                                draw_binary = ImageDraw.Draw(image_pil)
                                # >>>>>>>>>>> 小数点1
                                # point1_victor = Axis_proportion(0.56,0.61,0.91,0.98)

                                # draw_binary.rectangle((victor_screen_x1 + point1_victor.axis_left * (victor_screen_y2 - victor_screen_y1),
                                #                 victor_screen_y1 + point1_victor.axis_up * (victor_screen_y2 - victor_screen_y1),
                                #                 victor_screen_x1 + point1_victor.axis_right * (victor_screen_y2 - victor_screen_y1),
                                #                 victor_screen_y1 + point1_victor.axis_down * (victor_screen_y2 - victor_screen_y1)),
                                #                outline='white', width=3)

                                draw_binary.rectangle((295,505 , 325,530 ), outline='red', width=3)

                                point1_victor_arr = 255 * img_binary[505:530,295:325]
                                # 灰度化和二值化
                                y = (0.2126 * point1_victor_arr[:, :, 2] +
                                     0.7152 * point1_victor_arr[:, :, 1] +
                                     0.0722 * point1_victor_arr[:, :, 0])
                                # #
                                y[y >= 100] = 255
                                y[y < 100] = 0
                                point1_victor_arr[:, :, 0] = y
                                point1_victor_arr[:, :, 1] = y
                                point1_victor_arr[:, :, 2] = y

                                pixel_black = np.sum(point1_victor_arr == 0)
                                print('小数点1黑像素 is %d' % pixel_black)
                                print('小数点1总像素 is %d' % point1_victor_arr.size)
                                print('小数点1像素比值 is %f' % (pixel_black / point1_victor_arr.size))

                                if pixel_black / point1_victor_arr.size > point_proportion:
                                    point_flag = 1
                                    point_proportion = pixel_black / point1_victor_arr.size
                                    # img_test = Image.fromarray(point1_victor_arr.astype(np.uint8))
                                    # img_test.show()

                                # >>>>>>>>小数点2
                                draw_binary.rectangle((480, 505, 510, 530), outline='red', width=3)
                                point2_victor_arr = 255 * img_binary[505:530, 480:510]
                                # 灰度化和二值化
                                y = (0.2126 * point2_victor_arr[:, :, 2] +
                                     0.7152 * point2_victor_arr[:, :, 1] +
                                     0.0722 * point2_victor_arr[:, :, 0])
                                # #
                                y[y >= 100] = 255
                                y[y < 100] = 0
                                point2_victor_arr[:, :, 0] = y
                                point2_victor_arr[:, :, 1] = y
                                point2_victor_arr[:, :, 2] = y

                                pixel_black = np.sum(point2_victor_arr == 0)
                                print('小数点2黑像素 is %d' % pixel_black)
                                print('小数点2总像素 is %d' % point2_victor_arr.size)
                                print('小数点2像素比值 is %f' % (pixel_black / point2_victor_arr.size))

                                if pixel_black / point2_victor_arr.size > point_proportion:
                                    point_flag = 2
                                    point_proportion = pixel_black / point2_victor_arr.size
                                    # img_test = Image.fromarray(point2_victor_arr.astype(np.uint8))
                                    # img_test.show()

                                # >>>>>>>>>>小数点3
                                draw_binary.rectangle((665, 505, 695, 530), outline='red', width=3)
                                point3_victor_arr = 255 * img_binary[505:530, 665:695]
                                # 灰度化和二值化
                                y = (0.2126 * point3_victor_arr[:, :, 2] +
                                     0.7152 * point3_victor_arr[:, :, 1] +
                                     0.0722 * point3_victor_arr[:, :, 0])
                                # #
                                y[y >= 100] = 255
                                y[y < 100] = 0
                                point3_victor_arr[:, :, 0] = y
                                point3_victor_arr[:, :, 1] = y
                                point3_victor_arr[:, :, 2] = y

                                pixel_black = np.sum(point3_victor_arr == 0)
                                print('小数点3黑像素 is %d' % pixel_black)
                                print('小数点3总像素 is %d' % point3_victor_arr.size)
                                print('小数点3像素比值 is %f' % (pixel_black / point3_victor_arr.size))

                                if pixel_black / point3_victor_arr.size > point_proportion:
                                    point_flag = 3
                                    point_proportion = pixel_black / point2_victor_arr.size
                                    # img_test = Image.fromarray(point3_victor_arr.astype(np.uint8))
                                    # img_test.show()
                                point_proportion = 0.5
                                # image_pil.show()
                                # >>>>>>>>>>>>>> 伪造连接符
                                # point_add_front_vic = Axis_proportion(1.3, 1.5, 0.85, 0.9)
                                # point_add = np.ones((int(victor_screen_y1 + point_add_front_vic.axis_down * (victor_screen_y2 - victor_screen_y1)) -
                                #                      int(victor_screen_y1 + point_add_front_vic.axis_up * (victor_screen_y2 - victor_screen_y1)),
                                #                      int(victor_screen_x1 + point_add_front_vic.axis_right * (victor_screen_y2 - victor_screen_y1)) -
                                #                      int(victor_screen_x1 + point_add_front_vic.axis_left * (victor_screen_y2 - victor_screen_y1)),
                                #                      3), np.uint8)
                                # img[
                                # int(victor_screen_y1 + point_add_front_vic.axis_up * (
                                #             victor_screen_y2 - victor_screen_y1)) :
                                # int(victor_screen_y1 + point_add_front_vic.axis_down * (
                                #             victor_screen_y2 - victor_screen_y1)),
                                # int(victor_screen_x1 + point_add_front_vic.axis_left * (
                                #             victor_screen_y2 - victor_screen_y1)) :
                                # int(victor_screen_x1 + point_add_front_vic.axis_right * (
                                #             victor_screen_y2 - victor_screen_y1)),
                                # # int(axis_y1 + point_add_front.axis_up * (axis_x2 - axis_x1)):  # 0.92  # up
                                # # int(axis_y2 + point_add_front.axis_down * (axis_x2 - axis_x1)),  # 0.9   # down
                                # # int(axis_x1 + point_add_front.axis_left * (axis_x2 - axis_x1)):  # 0.4   # left
                                # # int(axis_x2 + point_add_front.axis_right * (axis_x2 - axis_x1))  # -0.45 # right
                                # ] = point_add * 0.20
                                # img_test2 = 255 * img
                                # img_test2 = Image.fromarray(img_test2.astype(np.uint8))
                                # # img_test2.show()
                                # <<<<<<<<<<<<<<<< 伪造连接符

                                #######################################################################################################################################################
                                # 示数区域

                                # num_victor = Axis_proportion(0.23,2,0.2,0.99)
                                # draw.rectangle(
                                #     (victor_screen_x1 + num_victor.axis_left * (victor_screen_y2 - victor_screen_y1),
                                #      victor_screen_y1 + num_victor.axis_up * (victor_screen_y2 - victor_screen_y1),
                                #      victor_screen_x1 + num_victor.axis_right * (victor_screen_y2 - victor_screen_y1),
                                #      victor_screen_y1 + num_victor.axis_down * (victor_screen_y2 - victor_screen_y1)),
                                #     outline='red', width=3)
                                # # 裁剪roi图像
                                # roi_SCR_arr = 255 * img[int(victor_screen_y1 + num_victor.axis_up * (victor_screen_y2 - victor_screen_y1)): int(victor_screen_y1 + num_victor.axis_down * (victor_screen_y2 - victor_screen_y1)),
                                #                     int(victor_screen_x1 + num_victor.axis_left * (victor_screen_y2 - victor_screen_y1)): int(victor_screen_x1 + num_victor.axis_right * (victor_screen_y2 - victor_screen_y1))]
                                # roi_SCR_height, roi_SCR_width = roi_SCR_arr.shape[:2]
                                #
                                # # 500外框
                                # new_roi_SCR_height = roi_SCR_height + 1000
                                # new_roi_SCR_width = roi_SCR_width + 1000
                                # new_roi_SCR_arr = np.zeros((new_roi_SCR_height, new_roi_SCR_width, 3), np.uint8)
                                #
                                # new_roi_SCR_arr[500:new_roi_SCR_height - 500, 500:new_roi_SCR_width - 500] = roi_SCR_arr
                                #
                                # roi_SCR_boxes, roi_SCRshow_res, _ = self.__call__(new_roi_SCR_arr, cls)
                                # SCRshow_index = 0

                                fina_res = []
                                all_res = detect.detect_qianxing_number()

                                # print(all_res)
                                for i in range(all_res.__len__()):
                                    if int(all_res[i][5]) == 1:
                                        fina_res.append(1)
                                    elif int(all_res[i][5]) == 9:
                                        fina_res.append(9)
                                    elif int(all_res[i][5]) == 0:
                                        fina_res.append(0)
                                    elif int(all_res[i][5]) == 8:
                                        fina_res.append(8)
                                    elif int(all_res[i][5]) == 3:
                                        fina_res.append(3)
                                    elif int(all_res[i][5]) == 4:
                                        fina_res.append(4)
                                    elif int(all_res[i][5]) == 2:
                                        fina_res.append(2)
                                    elif int(all_res[i][5]) == 7:
                                        fina_res.append(7)
                                    elif int(all_res[i][5]) == 5:
                                        fina_res.append(5)
                                    elif int(all_res[i][5]) == 6:
                                        fina_res.append(6)

                                ########################################################################################
                                # >>>>>>>>>>>>>>>> 示数 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('示  数：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('示  数：' + ' ')
                                    # <<<<<<<<<<<<<<<< 示数 <<<<<<<<<<<<<<<<<<<

                                    # if len(roi_numshow_back_res) != 0:
                                    #     for numshow_index in range(0, len(roi_numshow_front_res[0]) - 1):
                                    if len(fina_res) != 0:
                                        fina_res.reverse()
                                        with open('result.txt', 'a') as file:
                                            # >>>>>>>判断小数点位置>>>>>>>
                                            # num_res = roi_numshow_front_res[numshow_index][0]
                                            # num_res = num_res.replace('.','')
                                            # num_res =  int(''.join(fina_res))

                                            num_res = ''.join(map(str, fina_res))
                                            # print(result)
                                            # print(float(num_res))

                                            # next 为小数点
                                            if point_flag == 1:
                                                num_res = float(num_res) / 1000
                                            elif point_flag == 2:
                                                num_res = float(num_res) / 100
                                            elif point_flag == 3:
                                                num_res = float(num_res) / 10
                                            num_res = str(num_res)


                                            point_flag = 0  #
                                            # <<<<<<<判断小数点位置<<<<<<<
                                            file.write(num_res + '\n')  # roi_numshow_res[numshow_index][0]
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write(num_res + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # with open('result.txt', 'a') as file:
                                #     file.write('示  数：' + ' ')
                                # with open('log.txt', 'a') as file_log:
                                #     file_log.write('示  数：' + ' ')
                                #     if len(roi_SCRshow_res) != 0:
                                #         for SCRshow_index in range(0, len(roi_SCRshow_res[0]) - 1):
                                #             with open('result.txt', 'a') as file:
                                #                 # >>>>>>>判断小数点位置>>>>>>>
                                #                 num_res = roi_SCRshow_res[SCRshow_index][0]
                                #                 num_res = num_res.replace('.', '')
                                #                 print(float(num_res))
                                #                 if point_flag == 1:
                                #                     num_res = float(num_res) / 1000
                                #                 elif point_flag == 2:
                                #                     num_res = float(num_res) / 100
                                #                 elif point_flag == 3:
                                #                     num_res = float(num_res) / 10
                                #                 num_res = str(num_res)
                                #                 point_flag = 0  #
                                #                 # <<<<<<<判断小数点位置<<<<<<<
                                #                 file.write(num_res + '\n')  # roi_numshow_res[numshow_index][0]
                                #             with open('log.txt', 'a') as file_log:
                                #                 file_log.write(num_res + '\n')
                                #             #
                                #             #     file.write(roi_SCRshow_res[SCRshow_index][0] + '\n')  # roi_numshow_res[numshow_index][0]
                                #             # with open('log.txt', 'a') as file_log:
                                #             #     file_log.write(roi_SCRshow_res[SCRshow_index][0] + '\n')
                                #     else:
                                #         with open('result.txt', 'a') as file:
                                #             file.write('\n')
                                #         with open('log.txt', 'a') as file_log:
                                #             file_log.write('\n')
                                #######################################################################################
                                # 参数补充
                                # >>>>>>>>>>>>>>>> 欧姆 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧  姆：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧  姆：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧姆 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> 欧米伽 >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('欧米伽：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('欧米伽：' + ' ')
                                # <<<<<<<<<<<<<<<< 欧米伽 <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> nf >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  nf  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  nf  ：' + ' ')
                                # <<<<<<<<<<<<<<<< nf <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> mV >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write('  (m)V  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('  (m)V  ：' + ' ')
                                # <<<<<<<<<<<<<<<< mV <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # >>>>>>>>>>>>>>>> A/D >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' A/D ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/D ：' + ' ')
                                # <<<<<<<<<<<<<<<< A/D <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')


                                #######################################################################################################################################################
                                # μ/mA 区域
                                mA_victor = AxisProportion(1.6, 2, 0.35, 0.6)
                                draw.rectangle(
                                    (victor_screen_x1 + mA_victor.axis_left * (victor_screen_y2 - victor_screen_y1),
                                     victor_screen_y1 + mA_victor.axis_up * (victor_screen_y2 - victor_screen_y1),
                                     victor_screen_x1 + mA_victor.axis_right * (victor_screen_y2 - victor_screen_y1),
                                     victor_screen_y1 + mA_victor.axis_down * (victor_screen_y2 - victor_screen_y1)),
                                    outline='red', width=3)
                                # 裁剪ROI图像
                                roi_mA_arr = 255 * img[int(victor_screen_y1 + mA_victor.axis_up * (
                                            victor_screen_y2 - victor_screen_y1)): int(
                                    victor_screen_y1 + mA_victor.axis_down * (victor_screen_y2 - victor_screen_y1)),
                                                    int(victor_screen_x1 + mA_victor.axis_left * (
                                                                victor_screen_y2 - victor_screen_y1)): int(
                                                        victor_screen_x1 + mA_victor.axis_right * (
                                                                    victor_screen_y2 - victor_screen_y1))]
                                # 图像显示
                                # roi_mA_arr.show()
                                #######################################################################################################################################################
                                roi_mA_height, roi_mA_width = roi_mA_arr.shape[:2]

                                new_roi_mA_height = roi_mA_height + 1000
                                new_roi_mA_width = roi_mA_width + 1000
                                new_roi_mA_arr = np.zeros((new_roi_mA_height, new_roi_mA_width, 3),
                                                          np.uint8)

                                new_roi_mA_arr[500:new_roi_mA_height - 500,
                                500:new_roi_mA_width - 500] = roi_mA_arr

                                roi_mA_boxes, roi_mAshow_res, _ = self.__call__(new_roi_mA_arr, cls)
                                mAshow_index = 0

                                # >>>>>>>>>>>>>>>> (μ/m)A >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' (μ/m)A  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' (μ/m)A  ：' + ' ')
                                    if len(roi_mAshow_res) != 0:
                                        for mAshow_index in range(0, len(roi_mAshow_res[0]) - 1):
                                            with open('result.txt', 'a') as file:
                                                file.write(roi_mAshow_res[mAshow_index][0] + '\n')
                                            with open('log.txt', 'a') as file_log:
                                                file_log.write(roi_mAshow_res[mAshow_index][0] + '\n')
                                    else:
                                        with open('result.txt', 'a') as file:
                                            file.write('\n')
                                        with open('log.txt', 'a') as file_log:
                                            file_log.write('\n')
                                # <<<<<<<<<<<<<<<< (μ/m)A <<<<<<<<<<<<<<<<<<<

                                # >>>>>>>>>>>>>>>> A/M >>>>>>>>>>>>>>>>>>>
                                with open('result.txt', 'a') as file:
                                    file.write(' A/M  ：' + ' ')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write(' A/M  ：' + ' ')
                                # <<<<<<<<<<<<<<<< A/M <<<<<<<<<<<<<<<<<<<
                                with open('result.txt', 'a') as file:
                                    file.write('\n')
                                with open('log.txt', 'a') as file_log:
                                    file_log.write('\n')

                                # 图像显示
                                img_pil.show()

                ocr_res.append(tmp_res)
            return ocr_res
        elif det and not rec:
            ocr_res = []
            for idx, img in enumerate(imgs):
                dt_boxes, elapse = self.text_detector(img)
                tmp_res = [box.tolist() for box in dt_boxes]
                ocr_res.append(tmp_res)
            return ocr_res
        else:
            ocr_res = []
            cls_res = []
            for idx, img in enumerate(imgs):
                if not isinstance(img, list):
                    img = [img]
                if self.use_angle_cls and cls:
                    img, cls_res_tmp, elapse = self.text_classifier(img)
                    if not rec:
                        cls_res.append(cls_res_tmp)
                roi_num_res, elapse = self.text_recognizer(img)
                ocr_res.append(roi_num_res)
            if not rec:
                return cls_res
            return ocr_res

def meterocr(image):

    engine = PaddleOCR()


    result = engine.ocr(image,
                        det=True,  # 识别
                        rec=True,  # 检测
                        cls=True)  # 使用方向分类器识别180度旋转文字
    if result is not None:
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                logger.info(line)
    else:
        print("result is none")

    # 显示结果
    result = result[0]
    #image = Image.open(img_path).convert('RGB')
    # resize(image, image, Size(800, 784), 0, 0, INTER_LINEAR);
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)