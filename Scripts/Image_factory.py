import os

import cv2
import time


def cut_image(path):
    # 加载原始图像

    img = cv2.imread(path)

    # 获取原始图像的尺寸
    height, width, channels = img.shape
    crop_width = 1570
    start_time = time.time()

    # 计算裁剪区域
    left = (width - 1450) // 2
    top = 0
    right = left + crop_width
    bottom = height

    # 裁剪图像
    cropped_img = img[top:bottom, left:right]
    end_time = time.time()
    # 保存裁剪后的图像
    cv2.imwrite(path, cropped_img)

    print(f"裁剪图像耗时: {end_time - start_time:.6f} 秒")


if __name__ == "__main__":
    path = r"C:\Users\Administrator\Desktop\pics"
    file_walk = os.listdir(path)
    for file in file_walk:
        file1 = os.path.join(path, file)
        cut_image(file1)
