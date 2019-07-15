import cv2
import os
import numpy as np
import sys, getopt


def compose_image(dir, dir_num, img_num, start_x, start_y, small_img_x, small_img_y, matrix, n):
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


def pingjie_multilple(dir, img_number, img_dir_num, dir_num, img_num, start_x, start_y, small_img_x, small_img_y,  matrix):
    _x = int(img_number / img_num)
    _y = int(img_dir_num / dir_num)
    n = 0
    for y in range(_y):
        for x in range(_x):
            n += 1
            img = compose_image(dir, dir_num, img_num, start_x + img_num * x, start_y + dir_num * y, small_img_x, small_img_y, matrix, n)
            cv2.imwrite("final_imgs/" + str(n).zfill(6) + ".jpg", img)
            x += img_num
        y += dir_num
    return 0


def main(argv):
    dir_name = ''  # 目录路径
    dir_num = 0  # 每张图片合成所需文件夹数
    img_num = 0  # 每张图片合成所需小图片数
    small_img_x = 0  # 合成前图片列数
    small_img_y = 0  # 合成前图片行数
    try:
        opts, args = getopt.getopt(argv, "hd:n:m:x:y:", ["dir_name=", "dir_num=", "img_num=", "small_img_x=", "small_img_y="])
    except getopt.GetoptError:
        print('img_merge.py -d <dir_name> -n <dir_num> -m <img_num> -x <small_img_x> -y <small_img_y>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('img_merge.py -d <dir_name> -n <dir_num> -m <img_num> -x <small_img_x> -y <small_img_y>')
            print('Input_Example: python img_merge.py -d "E:/works/py_programs/photo_hecheng/21" -n 8 -m 8 -x 256 -y 256')
            sys.exit()
        elif opt in ("-d", "--dir_name"):
            dir_name = arg
        elif opt in ("-n", "--dir_num"):
            dir_num = int(arg)
        elif opt in ("-m", "--img_num"):
            img_num = int(arg)
        elif opt in ("-x", "--small_img_x"):
            small_img_x = int(arg)
        elif opt in ("-y", "--small_img_y"):
            small_img_y = int(arg)

    a = 0
    img_number = 0
    img_dir_num = 0
    start_x = 0
    start_y = 0
    matrix = [['' for i in range(8)] for j in range(8)]

    for root, dirs, files in os.walk(dir_name):
        if a == 0:
            img_dir_num = len(dirs)
            start_y = int(dirs[0])
        elif a == 1:
            img_number = len(files)
            start_x = int(files[0].split(".")[0])
            break
        a += 1
    pingjie_multilple(dir_name, img_number, img_dir_num, dir_num, img_num, start_x, start_y, small_img_x, small_img_y, matrix)


if __name__ == '__main__':
    main(sys.argv[1:])
