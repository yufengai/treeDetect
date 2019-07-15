import cv2
import os
import numpy as np


def compose_image(dir, dir_num, img_num, start_x, start_y, matrix, n):
    b = np.random.randint(0, 255, (small_img_y * img_num, small_img_x * dir_num), dtype=np.uint8)
    g = np.random.randint(0, 255, (small_img_y * img_num, small_img_x * dir_num), dtype=np.uint8)
    r = np.random.randint(0, 255, (small_img_y * img_num, small_img_x * dir_num), dtype=np.uint8)
    img = cv2.merge([b, g, r])

    orl_start_x = start_x
    orl_start_y = start_y

    for j in range(dir_num):
        for i in range(img_num):
            matrix[j][img_num - 1 - i] = (orl_start_y, orl_start_x)
            insert_img_dir = dir + "/" + str(orl_start_y) + "/" + str(orl_start_x) + ".png"
            insert_img = cv2.imread(insert_img_dir)
            img[small_img_x * (img_num - 1 - i): small_img_x + small_img_x * (img_num - 1 - i), small_img_y * j: small_img_y + small_img_y * j, :] = insert_img
            orl_start_x += 1
        orl_start_x = start_x
        orl_start_y += 1
    np.save("npy/" + str(n).zfill(6) + ".npy", matrix)
    return img


def pingjie_multilple(dir, dir_num, img_num, start_x, start_y, matrix):
    _x = int(img_number / img_num)
    _y = int(img_dir_num / dir_num)
    n = 0
    for y in range(_y):
        for x in range(_x):
            n += 1
            img = compose_image(dir, dir_num, img_num, start_x + img_num * x, start_y + dir_num * y, matrix, n)
            cv2.imwrite("final_imgs/" + str(n).zfill(6) + ".jpg", img)
            x += img_num
        y += dir_num
    return 0


dir = "E:/works/py_programs/photo_hecheng/21"
small_img_x = 256  # 合成前图片列数
small_img_y = 256  # 合成前图片行数
dir_num = 8  # 每张图片合成所需文件夹数
img_num = 8  # 每张图片合成所需小图片数
matrix = [['' for i in range(8)] for j in range(8)]

if __name__ == '__main__':
    # 变量初始化
    a = 0
    img_number = 0
    img_dir_num = 0
    start_x = 0
    start_y = 0

    for root, dirs, files in os.walk(dir):
        if a == 0:
            img_dir_num = len(dirs)
            start_y = int(dirs[0])
        elif a == 1:
            img_number = len(files)
            start_x = int(files[0].split(".")[0])
            break
        a += 1
    pingjie_multilple(dir, dir_num, img_num, start_x, start_y, matrix)
