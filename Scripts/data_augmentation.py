import os

import cv2
import random
from PIL import Image
from PIL import ImageEnhance
import numpy as np


def change_color(img):
    '''
    随机颜色增强
    :param img:
    :return:
    '''
    # 随机选择某种增强模式
    p = random.randint(0, 3)
    # 设置增强模式，这里分为了四种，可自行添加、删除
    a1 = random.uniform(0.8, 2)
    a2 = random.uniform(0.8, 1.4)
    a3 = random.uniform(0.8, 1.7)
    a4 = random.uniform(0.8, 2.5)
    img = Image.fromarray(img)
    # 这里使用了pillow的色彩增强api
    img = ImageEnhance.Color(img).enhance(a1) if p == 0 else img
    img = ImageEnhance.Brightness(img).enhance(a2) if p == 1 else img
    img = ImageEnhance.Contrast(img).enhance(a3) if p == 2 else img
    img = ImageEnhance.Sharpness(img).enhance(a4) if p == 3 else img
    img = np.array(img)

    return img


def random_horizontal_flip(image):
    '''
    随机水平翻转
    :param image:
    :return:
    '''
    sign = 0
    if random.random() < 0.5:
        _, w, _ = image.shape
        image = image[:, ::-1, :]
        # 也可以使用cv2.flip进行翻转
        sign = 1
    return image, sign


def image_preporcess(image, target_size):
    '''
    随机缩放
    :param image:
    :param target_size:
    :return:
    '''
    sign = 0
    if random.random() < 0.8:
        ih, iw = target_size
        h, w, _ = image.shape

        scale = min(iw / w, ih / h)
        nw, nh = int(scale * w), int(scale * h)
        image_resized = cv2.resize(image, (nw, nh))

        image_paded = np.full(shape=[ih, iw, 3], fill_value=128, dtype=np.uint8)
        dw, dh = (iw - nw) // 2, (ih - nh) // 2
        image_paded[dh:nh + dh, dw:nw + dw, :] = image_resized
        # image_paded = image_paded / 255.
        sign = 1
        return image_paded, sign
    else:
        return image, sign


def save_result(filepath, file, img_processed):
    """
    图片存储
    :param filepath: 存储路径
    :param file: 源文件
    :param img_processed: 处理后文件
    :return:
    """
    isExists = os.path.exists("./" + str(filepath) + '/') or os.path.exists(str(filepath) + '/')
    if not isExists:  # 判断如果文件不存在,则创建
        os.makedirs("./" + str(filepath) + '/')
        print("./" + str(filepath) + '/' + "目录创建成功")

    out = str(file.split('.')[0])
    # filename = "./" + filepath + '/%s.jpg' % (out)
    filename = filepath + '/%s.jpg' % (out)
    print('已匹配图片：' + filename)
    cv2.imwrite(filename, img_processed)


def cv_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    jpg_path = r"../data_processed3/pics/"  # 图片存放文件夹的路径
    save_path = r"../data_processed3/temps/"  # 图片处理后的存放路径
    file_walk = os.listdir(jpg_path)
    index = 1
    # for file in file_walk:
    #     # if file.endswith(".jpeg"):
    #     #     out = str(file.split('.')[0])
    #     #     oldname = jpg_path + file
    #     #     newname = jpg_path + '/%s.jpg' % (out)
    #     #     os.rename(oldname, newname)
    #
    #     # out = int(file.split('.')[0])
    #     oldname = jpg_path + file_walk[index]
    #     newname = jpg_path + '/%s.jpg' % str(index + 11)
    #     os.rename(oldname, newname)
    #
    #     index += 1

    for file in file_walk:
        file1 = os.path.join(jpg_path, file)  # 路径拼接
        img_rgb = cv2.imread(file1)

        # 此处为处理逻辑

        # 颜色随机增强
        # new_img = change_color(img_rgb)

        # 随机水平翻转
        # new_img, sign = random_horizontal_flip(img_rgb)

        # 随机缩放
        x, y = img_rgb.shape[0] / (1 + random.random()), img_rgb.shape[1] / (1 + random.random())
        new_img, sign = image_preporcess(img_rgb, [int(x), int(y)])


        # 显示图片
        # img_init = cv2.resize(img_rgb, (0, 0), fx=0.25, fy=0.25)
        # img_after = cv2.resize(new_img, (0, 0), fx=0.25, fy=0.25)
        # cv_show("img_init", img_init)
        # cv_show('img_after', img_after)

        # 保存图片
        # if sign == 1:
        #     save_result(save_path, file, new_img)


        cv2.imwrite(os.path.join(save_path, f'{index}.jpg'), new_img)
        # save_result(save_path, file, new_img)

        index += 1
