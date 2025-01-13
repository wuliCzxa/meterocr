from PIL import Image
import numpy as np
import cv2
import os
from skimage import color, filters
def img_niblack_binary(point_arr, thrshd_proportion=0.25, window_size=17, k=-0.2):
    # 转换为灰度图
    gray_image = color.rgb2gray(point_arr)

    # 使用 Niblack 阈值法
    binary = filters.threshold_niblack(gray_image, window_size=window_size, k=k)

    # 根据 Niblack 结果进行二值化
    y = np.zeros_like(binary)
    y[binary >= thrshd_proportion] = 255

    # 复制二值图到每个通道，保持形状一致
    binary_rgb = np.zeros_like(point_arr)
    binary_rgb[:, :, 0] = y
    binary_rgb[:, :, 1] = y
    binary_rgb[:, :, 2] = y

    return binary_rgb
def img_binary(point_arr, thrshd_proportion=0.25):
    # 灰度图   RGB
    y = 0.2126 * point_arr[:, :, 2] + 0.7152 * point_arr[:, :, 1] + 0.0722 * point_arr[:, :, 0]

    # y_max = y.max()
    # y_min = y.min()
    # thrshd = y_min + thrshd_proportion * (y_max - y_min)
    # y[y >= thrshd] = 255
    # y[y < thrshd] = 0
    # point_arr[:, :, 0] = y
    # point_arr[:, :, 1] = y
    # point_arr[:, :, 2] = y
    # return point_arr

    return y
def img_otsu_binary(point_arr):
    # 转换为灰度图
    gray_image = cv2.cvtColor(point_arr, cv2.COLOR_BGR2GRAY)

    # 使用 Otsu's 二值化
    _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 复制二值图到每个通道，保持形状一致
    point_arr[:, :, 0] = binary
    point_arr[:, :, 1] = binary
    point_arr[:, :, 2] = binary

    return point_arr
def img_sauvola_binary(point_arr, window_size=15, k=0.3):
    # 转换为灰度图
    gray_image = color.rgb2gray(point_arr)

    # 使用 Sauvola 阈值法
    binary = filters.threshold_sauvola(gray_image, window_size=window_size, k=k)

    # 将二值图复制到每个通道，保持形状一致
    binary_rgb = np.zeros_like(point_arr)
    binary_rgb[:, :, 0] = binary
    binary_rgb[:, :, 1] = binary
    binary_rgb[:, :, 2] = binary

    return binary_rgb
def improved_otsu(img, h=17, w=17, a=0.9, beta=0.9):
    # 将图片转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 步骤1: 计算整个图像的OTSU阈值
    T1, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 步骤2: 计算阴暗区域的OTSU阈值
    dark_part = gray[gray < T1]
    if len(dark_part) == 0:
        T2 = T1
    else:
        T2, _ = cv2.threshold(dark_part, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 步骤3: 判断像素点所处区域
    result = np.zeros_like(gray)
    for y in range(h, gray.shape[0] - h):
        for x in range(w, gray.shape[1] - w):
            local = gray[y-h:y+h+1, x-w:x+w+1]
            sum_above_T1 = np.sum(local > T1)
            if sum_above_T1 > a * 255 * (2*h+1) * (2*w+1):
                threshold = T1
            else:
                threshold = T2
            result[y, x] = 255 if gray[y, x] > threshold else 0

    # 步骤4: 改进OTSU算法明暗边界处噪点的去除
    kernel = np.ones((2*h+1, 2*w+1), np.uint8)
    mask = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
    result[mask == 0] = 0

    return result


def process_image(image, crop_coordinates, thrshd_proportion = 0.6):
    # 裁剪图片
    cropped_image = image.crop(crop_coordinates)
    # 转换为NumPy数组
    cropped_image_np = np.array(cropped_image)
    # 二值化处理
    cropped_image_np = img_binary(cropped_image_np, thrshd_proportion=thrshd_proportion)
    # 将处理后的图像转换回PIL图像
    processed_cropped_image = Image.fromarray(cropped_image_np.astype('uint8'))
    # 将处理后的图像放回原图中的相应位置
    image.paste(processed_cropped_image, crop_coordinates)
    # 返回截取图
    # return processed_cropped_image
    # 返回合成图
    return image
if __name__ == '__main__':

    list_17b = (1205, 1022, 3521, 2045)     # 0.55
    list_15b = (1319, 1007, 3538, 2004)     # 0.53
    list_15b_screen = (1288, 502, 3891, 2265)
    list_177c = (1293, 1443, 3171, 2114)    # 0.6
    list_115c = (1474, 1299, 3376, 1970)    # 0.6
    list_312 = (1070, 566, 2630, 1195)      # 0.5
    list_1508 = (1445, 692, 3404, 1493)     # 0.5
    list_kkyor = (1764, 1254, 2845, 1780)   # 0.5
    list_uni = (1536, 893, 3067, 1773)      # 0.7

    docu_img = '15b'
    list_meter = list_15b_screen
    thrshd_proportion = 0.7

    input_folder = 'F:\\0_meter\\' + docu_img  # 替换为您的输入文件夹路径
    output_folder = 'D:\\data_project\\binary\\' + docu_img  # 替换为您的输出文件夹路径

    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.bmp', '.jpg', '.png'))]

    for img_test in image_files:
        image_path = os.path.join(input_folder, img_test)
        output_image_path = os.path.join(output_folder, img_test)

        image = cv2.imread(image_path)

        # 旋转图像
        height, width = image.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))

        pil_rotated_image = Image.fromarray(cv2.cvtColor(rotated_image, cv2.COLOR_BGR2RGB))

        x1, y1, x2, y2 = list_meter
        crop_coordinates = (x1, y1, x2, y2)

        processed_image = process_image(pil_rotated_image, crop_coordinates, thrshd_proportion=thrshd_proportion)

        # 保存图像
        output_image_path = os.path.join(output_folder, img_test)
        processed_image.save(output_image_path)
        # print('ok')
