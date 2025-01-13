# ocr区域是numpy格式
# draw是pil
#############task#########
# num的ocr识别
# Ω的识别
# 词典弄清楚，以及copy、clear
# 各个参数 链接 自己改一下
# 文件命名规范
# self.__call__ draw部分，代码更简洁


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

from meterocr.func_ocr import file_result_path
from tools.infer import predict_system
from ppocr.utils.logging import get_logger
from ppocr.utils.utility import check_and_read, get_image_file_list
from ppocr.utils.network import maybe_download, download_with_progressbar, is_link, confirm_model_dir_url
from tools.infer.utility import draw_ocr, str2bool, check_gpu
from ppstructure.utility import init_args, draw_structure_result
from ppstructure.predict_system import StructureSystem, save_structure_res, to_excel
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from func_ocr import *
import gui
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

    # for action in parser._actions:
    #     if action.dest in [
    #             'rec_char_dict_path', 'table_char_dict_path', 'layout_dict_path'
    #     ]:
    #         action.default = None
    #if mMain:
    return parser.parse_args()
    # else:
    #     inference_args_dict = {}
    #     for action in parser._actions:
    #         inference_args_dict[action.dest] = action.default
    #return argparse.Namespace(**inference_args_dict)
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
        # >>>>>>>>>>>>>>>>>>>>>>>>电表型号>>>>>>>>>>>>>>>>>>>>>>>>>>
        list_17b = ['17B']
        list_15b = ['15B+']
        list_1508 = ['1508 INSULATION TESTER', '1508 INSULATION TESTER', '1508 INSULATIONTESTER']
        list_115c = ['115C']
        list_177c = ['177CTRUERMSMULTIMETER','177C TRUERMSMULTIMETER']
        list_312 = ['312CLAMPMETER','312 CLAMPMETER']
        list_kkyor = ['KKYORITSU', 'KYORITSU']
        list_megohm = ['DIGITALMEGOHM', 'DIGITAL MEGOHM']
        list_4000counts = ['4000 Counts', '4000Counts']
        list_victor6800 = ['VICTOR6800', 'VICIOR6800', 'VICTOR 6800', 'ICIOR 6800', 'ICIOR6800', 'CIOR6800']
        list_victor = ['AC1200AMAX']

        # 二值化路径
        im_binary_path = "D:\\newmeterocr\\meterocr\\logs\\img\\"
        im_binary_name = 'test.bmp'
        if not os.path.exists(im_binary_path):
            os.makedirs(im_binary_path)
        full_binary_path = os.path.join(im_binary_path, im_binary_name)

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

                draw = ImageDraw.Draw(img_pil)  #
                tmp_res = [[box.tolist(), res] for box, res in zip(dt_boxes, roi_num_res)]

                try:
                    with open(file_log_path, 'r') as file_log:
                        log_content = file_log.read()
                except FileNotFoundError:
                    log_content = ""

                '''***************************进行型号识别*******************************'''

                # # 添加新的检测框区域
                # new_box = [100, 100, 200, 200]  # 示例：左上角坐标为(100, 100)，右下角坐标为(200, 200)
                # draw.rectangle(new_box, outline="red")
                #
                # # 遍历 ROI 裁剪区域
                # for idx_res, (element_res, _) in enumerate(roi_num_res):
                #     if isinstance(element_res, list):
                #         element_res = ", ".join(element_res)  # 如果型号是一个列表，将其转换为字符串
                #     draw.text((new_box[0], new_box[1] + idx_res * 20), element_res, fill="blue")  # 将型号写入新的检测框区域
                #
                #     # 检查是否在当前 ROI 区域内
                #     if is_inside(new_box, dt_boxes[idx_res]):
                #     # 查找是否匹配列表list_17b中的元素
                #     found_match = False  # 标记是否找到
                #     for element_meter in list_17b:
                #         if element_meter in element_res:
                #             found_match = True
                #             axis_model = dt_boxes[idx_res]
                #             with open(file_result_path, 'w') as file:
                #                 file.truncate(0)  # 清空文件内
                for idx_res, (element_res, _) in enumerate(roi_num_res):

                    found_match = False # 标记是否找到
                    # 17bMax
                    for element_meter in list_17b:
                        if element_meter in element_res:
                            found_match = True
                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # 型号
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'FLUKE 17B MAX')

                            # 屏幕区域
                            screen_meter = Axis(axis_model, -0.5, 0, 0.15, 1.1)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red', width=3)


                            # 小数点
                            point_meter = Axis(axis_model, -0.15, -1.1, 0.88, 0.9)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.3, 0.6])


                            # 示数
                            num_meter = Axis(axis_model, -0.5, -0.15, 0.4, 0.93)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)

                            draw.rectangle(num_meter.get_axis_arr(), outline='red',width=3)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, 0.7, -0.1, 0.3, 0.37)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0, 0.3, 0.6])
                            ohm_meter = Axis(axis_model, 0.6, -0.1, 0.3, 0.37)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)

                            # nf
                            nf_meter = Axis(axis_model, 0.78, 0, 0.45, 0.5)
                            new_roi_arr = get_roi_arr(draw, img, nf_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_nf(roi_show_res)

                            # mv
                            mv_meter = Axis(axis_model, 0.78, 0, 0.57, 0.60)
                            new_roi_arr = get_roi_arr(draw, img, mv_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_mv(roi_show_res)

                            # AC、DC 区域
                            ad_meter = Axis(axis_model, 0.78, 0, 0.67, 0.78)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ 区域
                            miu_meter = Axis(axis_model, 0.75, 0, 0.85, 0.9)
                            new_roi_arr = get_roi_arr(draw, img, miu_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_miu_ma(roi_show_res)

                            # A/M 区域
                            am_meter = Axis(axis_model, 0, -0.45, 0.95, 1)
                            new_roi_arr = get_roi_arr(draw, img, am_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_auto_manual(roi_show_res)

                            # img_pil.show()
                            break
                    # 15b+
                    for element_meter in list_15b:
                        if element_meter in element_res:
                            found_match = True
                            axis_model = dt_boxes[idx_res]

                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # >>>>>>>>>>>>>>>> 型号 >>>>>>>>>>>>>>>>>>>
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'FLUKE 15b+')
                            # <<<<<<<<<<<<<<<< 型号 <<<<<<<<<<<<<<<<<<<

                            # 屏幕区域
                            screen_meter = Axis(axis_model, -0.60, 0.10, 0.15, 1.2)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red',width=3)

                            # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                            point_meter = Axis(axis_model, -0.20, -1.15, 1.02, 1.04)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.34, 0.69])
                            # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                            # 示数ocr
                            num_meter = Axis(axis_model, - 0.58, -0.13, 0.48, 1.03)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, 0.7, -0.1, 0.3, 0.37)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0, 0.3, 0.6])
                            ohm_meter = Axis(axis_model, 0.6, -0.1, 0.3, 0.37)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)

                            # nf
                            save_exist_text('nf')

                            # mv
                            mv_meter = Axis(axis_model, 0.87, 0.06, 0.64, 0.70)
                            new_roi_arr = get_roi_arr(draw, img, mv_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_mv(roi_show_res)

                            # AC、DC 区域
                            ad_meter = Axis(axis_model, 0.88, 0.06, 0.75, 0.90)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ 区域
                            miu_meter = Axis(axis_model, 0.81, 0.05, 0.93, 1.0)
                            new_roi_arr = get_roi_arr(draw, img, miu_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_miu_ma(roi_show_res)

                            # A/M 区域
                            am_meter = Axis(axis_model, -0.12, -0.46, 1.08, 1.14)
                            new_roi_arr = get_roi_arr(draw, img, am_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_auto_manual(roi_show_res)

                            # img_pil.show()
                            break
                    # 1508 IN
                    for element_meter in list_1508:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # >>>>>>>>>>>>>>>> 型号 >>>>>>>>>>>>>>>>>>>
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'FLUKE 1508')
                            # <<<<<<<<<<<<<<<< 型号 <<<<<<<<<<<<<<<<<<<
                            # 屏幕区域
                            screen_meter = Axis(axis_model, -0.55, 0.13, 0.16, 1.2)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red',width=3)

                            # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                            point_meter = Axis(axis_model, -0.13, -1.05, 0.68, 0.7)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.25, 0.53])
                            # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                            # 示数区
                            num_meter = Axis(axis_model, -0.5, -0.25, 0.3, 0.72)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)
                            draw.rectangle(num_meter.get_axis_arr(), outline='red', width=3)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, 0.7, -0.1, 0.3, 0.37)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0, 0.3, 0.6])
                            ohm_meter = Axis(axis_model, 0.6, -0.1, 0.3, 0.37)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)

                            # nf
                            save_exist_text('nf')

                            # mv
                            save_exist_text('mv')

                            # VAC、VDC 区域
                            ad_meter = Axis(axis_model, 0.8, 0.1, 0.54, 0.65)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ 区域
                            save_exist_text('miu')

                            # A/M 区域
                            save_exist_text('am')

                            # 右下角数字区
                            num_corner_meter = Axis(axis_model, 0.7, -0.1, 1., 1.2)
                            new_roi_arr = get_roi_arr(draw, img, num_corner_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_num_corner(roi_show_res)

                            # 右下角数字区
                            word_corner_meter = Axis(axis_model, 0.9, 0.1, 1., 1.2)
                            new_roi_arr = get_roi_arr(draw, img, word_corner_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_num_corner(roi_show_res)

                            # img_pil.show()
                            break
                    # 115c
                    for element_meter in list_115c:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # >>>>>>>>>>>>>>>> 型号 >>>>>>>>>>>>>>>>>>>
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'FLUKE 115C')
                            # <<<<<<<<<<<<<<<< 型号 <<<<<<<<<<<<<<<<<<<

                            # 屏幕区域
                            screen_meter = Axis(axis_model, -2.24, 3.16, 0.7, 3.36)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red',width=3)

                            # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                            point_meter = Axis(axis_model, -0.61, -1.39, 2.68, 2.65)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 1.16, 2.31])
                            # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                            # 示数区
                            num_meter = Axis(axis_model, -2.24, 1.9, 1.14, 2.57)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)
                            draw.rectangle(num_meter.get_axis_arr(), outline='red', width=3)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, 0.7, -0.1, 0.3, 0.37)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0, 0.3, 0.6])
                            ohm_meter = Axis(axis_model, 0.6, -0.1, 0.3, 0.37)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)
                            # save_exist_text('ohm')

                            # nf
                            save_exist_text('nf')

                            # mv
                            mv_meter = Axis(axis_model, 2.9, 3.16, 1.44, 1.55)
                            new_roi_arr = get_roi_arr(draw, img, mv_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_mv(roi_show_res)

                            # AC、DC 区域
                            ad_meter = Axis(axis_model, 2.9, 3.16, 1.95, 1.96)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # # μ 区域
                            save_exist_text('miu')

                            # A/M 区域
                            am_meter = Axis(axis_model, -0.85, 0.78, 2.96, 2.99)
                            new_roi_arr = get_roi_arr(draw, img, am_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_auto_manual(roi_show_res)

                            # img_pil.show()
                            break
                    # 177c
                    for element_meter in list_177c:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # >>>>>>>>>>>>>>>> 型号 >>>>>>>>>>>>>>>>>>>
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'FLUKE 177c')
                            # <<<<<<<<<<<<<<<< 型号 <<<<<<<<<<<<<<<<<<<
                            # 屏幕区域
                            screen_meter = Axis(axis_model, -0.55, 0.08, 0.15, 0.82)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red', width=3)

                            # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                            point_meter = Axis(axis_model, -0.125, -1.07, 0.6, 0.6)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.265, 0.53])
                            # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                            # 示数ocr
                            num_meter = Axis(axis_model, - 0.5, -0.3, 0.3, 0.63)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)
                            draw.rectangle(num_meter.get_axis_arr(), outline='red', width=3)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, 0.7, -0.1, 0.17, 0.18)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0, 0.3, 0.6])
                            ohm_meter = Axis(axis_model, 0.6, -0.1, 0.17, 0.18)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)

                            # nf
                            save_exist_text('nf')

                            # mv
                            mv_meter = Axis(axis_model, 0.72, 0.02, 0.3, 0.36)
                            new_roi_arr = get_roi_arr(draw, img, mv_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_mv(roi_show_res)

                            # VAC、VDC 区域
                            ad_meter = Axis(axis_model, 0.73, -0.01, 0.41, 0.43)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ 区域
                            # miu_meter = Axis(axis_model, 0.81, 0.05, 0.93, 1.0)
                            # new_roi_arr = get_roi_arr(draw, img, miu_meter)
                            # roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            # save_miu_ma(roi_show_res)

                            # A/M 区域
                            am_meter = Axis(axis_model, -0.22, -0.4, 0.69, 0.72)
                            new_roi_arr = get_roi_arr(draw, img, am_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_auto_manual(roi_show_res)

                            # img_pil.show()
                            break
                    # 312clamp meter
                    for element_meter in list_312:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # 型号
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'FLUKE 312 CLAMP METER')

                            # 屏幕区域
                            screen_meter = Axis(axis_model, -0.75, -0.05, -1.15, -0.28)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red', width=3)

                            # 小数点
                            point_meter = Axis(axis_model, -0.3, -1.25, -0.54, -0.51)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.33, 0.66])

                            # 示数ocr
                            num_meter = Axis(axis_model, - 0.7, -0.27, -0.95, -0.45)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)
                            draw.rectangle(num_meter.get_axis_arr(), outline='red', width=3)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, 0.7, -0.04, 0.35, 0.43)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0, 0.3, 0.6])
                            ohm_meter = Axis(axis_model, 0.6, -0.04, 0.35, 0.43)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)

                            # nf
                            save_exist_text('nf')

                            # mv
                            mv_meter = Axis(axis_model, 0.75, -0.17, -0.95, -0.9)
                            new_roi_arr = get_roi_arr(draw, img, mv_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_mv(roi_show_res)

                            # AC、DC 区域
                            ad_meter = Axis(axis_model, 0.75, -0.05, -0.74, -0.6)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ 区域
                            miu_meter = Axis(axis_model, 0.8, -0.1, -0.95, -0.9)
                            new_roi_arr = get_roi_arr(draw, img, miu_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_miu_ma(roi_show_res)

                            # A/M 区域
                            am_meter = Axis(axis_model, 0.65, -0.05, -0.5, -0.5)
                            new_roi_arr = get_roi_arr(draw, img, am_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_auto_manual(roi_show_res)

                            # img_pil.show()
                            break
                    # kkyor
                    for element_meter in list_kkyor:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # 型号
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'KKYORITSU')

                            # 屏幕区域
                            screen_meter = Axis(axis_model, -0.46, 0.18, 0.21, 0.63)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red',width=3)

                            # 小数点
                            point_meter = Axis(axis_model, -0.14, -1.06, 0.64, 0.56)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.32, 0.60], thrshd_proportion=0.5)

                            # 示数ocr
                            num_meter = Axis(axis_model, - 0.23, -0.2, 0.25, 0.6)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)
                            draw.rectangle(num_meter.get_axis_arr(), outline='red', width=3)

                            # MΩ 区域
                            save_exist_text('ohm')

                            # nf
                            save_exist_text('nf')

                            save_exist_text('mv')

                            ad_meter = Axis(axis_model, -0.46, -1.26, 0.53, 0.53)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ 区域
                            miu_meter = Axis(axis_model, 0.77, 0.05, 0.3, 0.33)
                            new_roi_arr = get_roi_arr(draw, img, miu_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_miu_ma(roi_show_res)

                            # A/M 区域
                            save_exist_text('am')

                            # img_pil.show()
                            break
                    # 数字兆欧表
                    for element_meter in list_megohm:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # 型号
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'BY2671 数字兆欧表')
                            # >>>>>>>>>>>>>>> 记录小数点 >>>>>>>>>>>>>>>>>>
                            point_meter = Axis(axis_model, 0.19, 0.24, 0.557, 0.563)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.32, 0.65],point_proportion=0.08)
                            # <<<<<<<<<<<<<<<< 记录小数点 <<<<<<<<<<<<<<<<<<

                            # 示数区域
                            num_meter = Axis(axis_model, -0.13, 0.12, 0.20, 0.63)
                            print(num_meter.get_axis_arr())
                            new_roi_arr = get_roi_arr(draw, img, num_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_num_ocr(roi_show_res, point_flag)

                            '''******************箱式数字兆欧表--灯（开始）*************************'''
                            # light on/off
                            light_on_figure = Axis(axis_model, 0.45, 0.65, 0.95, 1.15)
                            draw.rectangle(light_on_figure.get_axis_arr(), outline='green', width=5)

                            # light 500v
                            light_500_figure = Axis(axis_model, -0.05, 0.15, 1.25, 1.45)
                            draw.rectangle(light_500_figure.get_axis_arr(), outline='green', width=5)

                            # light 1000v
                            light_1000_figure = Axis(axis_model, 0.15, 0.35, 1.65, 1.85)
                            draw.rectangle(light_1000_figure.get_axis_arr(),outline='green', width=5)

                            # light 2000v
                            light_2000_figure = Axis(axis_model, 0.85, 1.05, 1.65, 1.85)
                            draw.rectangle(light_2000_figure.get_axis_arr(),outline='green', width=5)

                            # light 2500v
                            light_2500_figure = Axis(axis_model, 1.05, 1.25, 1.25, 1.45)
                            draw.rectangle(light_2500_figure.get_axis_arr(),outline='green', width=5)

                            '''******************箱式数字兆欧表--灯（结束）*************************'''

                            save_exist_text('ohm')
                            save_exist_text('nf')
                            save_exist_text('mv')
                            save_exist_text('ad')
                            save_exist_text('miu')
                            save_exist_text('am')

                            # img_pil.show()
                            break
                    # 4000 counts
                    for element_meter in list_4000counts:
                        if element_meter in element_res:
                            found_match = True

                            axis_model = dt_boxes[idx_res]
                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # 型号
                            model_meter = Axis(axis_model)
                            draw.rectangle(model_meter.get_axis_arr(), outline='red', width=3)
                            save_exist_text('型号', 'UNI 4000 count')

                            # 屏幕区域
                            screen_meter = Axis(axis_model, -1.6, 0.1, -2, -0.3)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red',width=3)

                            # 小数点
                            point_meter = Axis(axis_model, -0.72, -1.58, -0.53, -0.58)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.54, 1.1])
                            # 示数yolo
                            num_meter = Axis(axis_model, -1.3, 0.1, -1.7, -0.5)
                            img_store(img, num_meter, full_binary_path, binary=True, thrshd_proportion=0.7)
                            fina_res = table_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)
                            draw.rectangle(num_meter.get_axis_arr(), outline='red', width=3)

                            # MΩ 区域
                            ohm_self = Axis(axis_model, -0.7, -1.5, -2, -1.85)
                            point_ohm = process_points(draw, img, ohm_self, point_list=[0],
                                                       point_proportion=0.2, thrshd_proportion=0.4)
                            img_store(img, ohm_self, full_binary_path, binary=True, thrshd_proportion=0.4)

                            ohm_meter = Axis(axis_model, -0.85, -1.5, -2, -1.85)
                            new_roi_arr = get_roi_arr(draw, img, ohm_meter, binary=True, thrshd_proportion=0.4)
                            img_store(img, ohm_meter, full_binary_path, binary=True, thrshd_proportion=0.4)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ohm(roi_show_res, point_ohm)

                            # nf
                            # save_exist_text('nf')

                            # 单位前半部分
                            unit_roi_1 = Axis(axis_model, -0.2, -0.9, -2, -1.85)
                            new_roi_arr = get_roi_arr(draw, img, unit_roi_1)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            if len(roi_show_res) != 0:
                                unit_word_1 = roi_show_res[0][0]
                            else:
                                unit_word_1 = ''
                            # 单位后半部分
                            unit_roi_2 = Axis(axis_model, 0.1, -0.5, -2, -1.85)
                            new_roi_arr = get_roi_arr(draw, img, unit_roi_2, binary=True, thrshd_proportion=0.5)
                            # img_store(img, unit_roi_2, full_binary_path, binary=True, thrshd_proportion=0.5)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            if len(roi_show_res) != 0:
                                unit_word_2 = roi_show_res[0][0]
                            else:
                                unit_word_2 = ''
                            save_unit_1_2(unit_word_1, unit_word_2)

                            # AC、DC 区域
                            ad_meter = Axis(axis_model, -1.6, -2.1, -1.3, -0.95)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # A/M 区域
                            am_meter = Axis(axis_model, -1.6, -1.2, -0.43, -0.3)
                            new_roi_arr = get_roi_arr(draw, img, am_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_auto_manual(roi_show_res)

                            # HZ区域
                            hz_meter = Axis(axis_model, -0.5, -1.2, -2, -1.85)
                            new_roi_arr = get_roi_arr(draw, img, hz_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_hz(roi_show_res)

                            # img_pil.show()
                            break
                    # victor 6800(N)
                    for element_meter in list_victor6800:
                        if element_meter in element_res:
                            found_match = True

                            with open(file_result_path, 'w') as file:
                                file.truncate(0)
                            # 型号
                            save_exist_text('型号', 'VICTOR 6800')

                            # axis_model = x1, y1, x2, y2
                            axis_model = [[0, 0], [0, 0], [0, 0]]
                            axis_model[0][0], axis_model[0][1], axis_model[2][0], axis_model[2][1] = detect.detect_qianxing_screen()

                            # 屏幕
                            screen_meter = Axis(axis_model)
                            draw.rectangle(screen_meter.get_axis_arr(), outline='red', width=3)
                            img_store(img, screen_meter, full_binary_path, binary=True, thrshd_proportion=0.55)
                            # 示数
                            fina_res = victor6800_yolo(full_binary_path)
                            save_num_yolo(fina_res, point_flag)

                            # 小数点
                            point_meter = Axis(axis_model, 0.24, -0.73, 0.425, -0.01)
                            point_flag = process_points(draw, img, point_meter, point_list=[0, 0.16, 0.32])

                            save_exist_text('ohm')
                            save_exist_text('nf')
                            save_exist_text('mv')

                            # AC/DC
                            ad_meter = Axis(axis_model, 0, -0.87, 0.17, -0.15)
                            new_roi_arr = get_roi_arr(draw, img, ad_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_ac_dc(roi_show_res)

                            # μ/mA 区域
                            miu_meter = Axis(axis_model, 0.76, -0.07, 0.17, -0.156)
                            new_roi_arr = get_roi_arr(draw, img, miu_meter)
                            roi_boxes, roi_show_res, _ = self.__call__(new_roi_arr, cls)
                            save_miu_ma(roi_show_res)

                            save_exist_text('am')

                            break

                res_store()
                dic_unit_copy.clear()
                read_txt_file(file_result_path)
                # 图像显示
                # img_pil.show()

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

    #返回所需文本
    return txts
    '''
     [[[2617.0, 735.0], [4247.0, 753.0], [4245.0, 890.0], [2616.0, 872.0]],('15B+ DIGITALMULTIMETER', 0.9164012670516968)]
    '''