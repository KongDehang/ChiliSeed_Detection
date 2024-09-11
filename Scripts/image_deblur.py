import numpy as np
import cv2
from scipy.signal import convolve2d


def motion_kernel(length, angle):
    kern = np.ones((1, length), np.float32)
    c, s = np.cos(angle), np.sin(angle)
    A = np.array([[c, -s, 0], [s, c, 0]], dtype=np.float32)
    sz = length // 2
    A[:, 2] = (sz, sz) - np.dot(A[:, :2], ((length - 1) * 0.5, 0))
    kern = cv2.warpAffine(kern, A, (length, length), flags=cv2.INTER_CUBIC)
    return kern


def wiener_filter(img, kernel, K):
    kernel /= np.sum(kernel)
    dummy = np.copy(img)
    dummy = np.fft.fft2(dummy)
    kernel = np.fft.fft2(kernel, s=img.shape)
    kernel = np.conj(kernel) / (np.abs(kernel) ** 2 + K)
    dummy = dummy * kernel
    dummy = np.abs(np.fft.ifft2(dummy))
    return dummy


def deblur_image(img, kernel_size=15, angle=0, snr=1000):
    kernel = motion_kernel(kernel_size, angle)
    deblurred = np.zeros_like(img, dtype=np.float32)
    for i in range(3):  # 处理每个颜色通道
        deblurred[:, :, i] = wiener_filter(img[:, :, i], kernel, 1 / snr)
    return np.clip(deblurred, 0, 255).astype(np.uint8)


# 主函数
if __name__ == "__main__":
    # 读取模糊图像
    blurred_img = cv2.imread(r'E:\ADataset\datasets\videosets\pics\72-1200-2.jpg')

    # 去模糊处理
    deblurred_img = deblur_image(blurred_img, kernel_size=15, angle=np.pi / 4)

    # 显示结果
    cv2.imshow('Original Blurred', blurred_img)
    cv2.imshow('Deblurred', deblurred_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 保存结果
    cv2.imwrite(r'E:\ADataset\datasets\videosets\pics\72-1200-2deblur.jpg', deblurred_img)
