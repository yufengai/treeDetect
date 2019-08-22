import cv2
import os
import numpy as np
import sys, getopt
import argparse
import logging
import time
import re

name_index = 0
logging.basicConfig(level=logging.INFO)


def parse_argment():
    parse = argparse.ArgumentParser()
    parse.add_argument("-d", "--dir_name", help="where picture is store", default="/home/data/tree/tile/0722/")
    parse.add_argument("-x", "--numx", default=8, type=int, help="num of x want to merger")
    parse.add_argument("-y", "--numy", default=8, type=int, help="num of y want to merger")
    parse.add_argument("-m", "--sizew", default=256, type=int, help="tile picture size w")
    parse.add_argument("-n", "--sizeh", default=256, type=int, help="tile picture size h")
    parse.add_argument("-b", "--batch", type=int, help="batch merge", default=0)
    parse.add_argument("-s", "--dest_dir", default=None, help="where merge pic to save")
    parse.add_argument("-f", "--file_dir", default=None, help="where merge xy to save")
    parse.add_argument("-p", "--npy_dir", default=None, help="where merge xy to save")

    args = parse.parse_args()
    return args


def toint(ele):
    if ele.isdigit():
        return int(ele)
    else:
        num = re.sub(r'\D+', "", ele)
        return int(num)


def is_list_continue(lst):
    new = list(map(toint, lst))
    for i in range(len(new) - 1):
        v1 = new[i]
        v2 = new[i + 1]
        if v1 + 1 != v2:
            return False
    return True


def check_cross(lst_left, lst_right):
    cross = set(lst_left) & set(lst_right)
    if len(cross) > 0:
        return True
    return False


def mapPng(ele):
    if ele.endswith((".png", ".jpg")):
        return True
    return False


def check_file_name(path):
    """
    检查文件是否符合连续性要求，并返回文件链表
    """
    dir2file = {}
    # 1. 选定最大级别
    paths_scale = os.listdir(path)
    paths_scale = sorted(list(filter(str.isdigit, paths_scale)))
    con = is_list_continue(paths_scale)
    if not con:
        logging.error("input scale dir path is not right")

    # 2. 获取所有的x目录
    path_scale = os.path.join(path, paths_scale[-1])
    paths_x = sorted(os.listdir(path_scale))
    con = is_list_continue(paths_x)
    if not con:
        logging.error("input x dir path is not right:$s", paths_x)
    # 获取每个y
    for path_x in paths_x:
        path_x = os.path.join(path_scale, path_x)
        files = os.listdir(path_x)
        files_con = sorted(list(filter(mapPng, files)))
        if is_list_continue(files_con):
            dir2file[path_x] = files_con
        else:
            logging.error("input y dir path is not right:%s", files)

    return dir2file


def align_pos(lst, numx, numy):
    # 处理第一张图片
    # 获取最小的元素
    minname = "9999999.png"
    maxname = "0000000.png"
    indexmin = 0
    indexmax = 0
    for i, m in enumerate(lst):
        tmpmin = min(m)
        tmpmax = max(m)
        if minname > tmpmin:
            minname = tmpmin
            indexmin = i
        if maxname < tmpmax:
            maxname = tmpmax
            indexmax = i
    logging.debug("----%d,%d", indexmin, indexmax)
    # 创建二维数组，所有图片都已经对其
    all_pic = sorted(list(set(lst[indexmin]) | set(lst[indexmax])))
    maxlen = len(all_pic)
    my, ny = divmod(len(all_pic), numy)
    if ny > 0:
        my += 1
        maxlen = numy * my
    alin_pos = [['None'] * maxlen for i in range(numx)]
    for i, pics in enumerate(lst):
        first = pics[0]
        index_first = all_pic.index(first)
        alin_pos[i][index_first:index_first + len(pics)] = pics[:]

    return alin_pos, maxlen


def merge_pic(dir2file, numx, numy, imgx, imgy, pic_dir, file_dir, npy_dir, batch):
    """
    合成图片数组
    :param dir2file: 字典，key是x，value是y列表
    :param numx:
    :param numy:
    :param imgx:
    :param imgy:
    :return:
    """
    # 1. 对x分块
    # 把所有的x取出来
    keys = sorted(dir2file.keys())
    # 判断x可以生成多少图片
    mx, nx = divmod(len(keys), numx)
    # 对x指定长度合成
    dct_image = {}
    dict_xy = {}
    for x in range(mx + 1):
        need_keys = []
        lst_epool = []
        if (x + 1) * numx > len(keys):
            need_keys = keys[::-1][0:numx][::-1]
        else:
            need_keys = keys[x * numx: (x + 1) * numx]
        for key in need_keys:
            # 按照顺序取出y轴
            lst_epool.append((sorted(dir2file[key])))
        # 生成对其列表
        right_pos, maxlen = align_pos(lst_epool, numx, numy)
        # 保存到文件中
        save_image_and_xy(right_pos, need_keys, numx, numy, imgx, imgy, x, pic_dir, file_dir, npy_dir, batch)
    # save_image_and_xy_to_file(dct_image, dict_xy)
    # 2. 对剩余的x做处理
    return


def save_image_and_xy_to_file(dct_image, dct_xy):
    for key, img in dct_image.items():
        cv2.imwrite(key + ".jpg", img)
    for key, lst_xy in dct_xy.items():
        with open(key + ".txt", "w") as f:
            for xy in lst_xy:
                for i in xy:
                    f.write(i)
                    f.write('\t')
                f.writelines('\n')


def save_image_and_xy(lst_need_tile, x_keys, numx, numy, imgx, imgy, xindex, pic_dir, file_dir, npy_dir, batch):
    global name_index
    # 循环所有x值
    # TODO 需要做异常判断
    county, mod = divmod(len(lst_need_tile[0]), numy)

    # 判断需要多少个图像
    for y in range(county):
        lst_xy = []
        matrix = [[("", "") for _ in range(numx)] for _ in range(numy)]
        img = np.full((numx * imgx, numy * imgy, 3), 0, np.uint8)
        for iy, tiles in enumerate(lst_need_tile):
            # for tile in tiles:  注意方向
            need_tile = tiles[y * numy:(y + 1) * numy][::-1]
            for ix, t in enumerate(need_tile):
                if t == "None":
                    continue
                infile = os.path.join(x_keys[iy], t)
                image = cv2.imread(infile)
                # TODO why

                img[ix * imgy:(ix + 1) * imgy, iy * imgx:(iy + 1) * imgx, :] = image
                lst_xy.append([os.path.basename(x_keys[iy]), os.path.splitext(t)[0]])
                matrix[iy][numx - ix - 1] = (os.path.basename(x_keys[iy]), os.path.splitext(t)[0])
        # 保存图片以及xy坐标

        logging.info("merge %s picture!", str(batch).zfill(5) + str(xindex).zfill(3) + str(y).zfill(3) + ".png")
        # 需要设置图像质量 png压缩级别，默认是3  jpg设置图像质量，默认是95 [int(cv2.IMWRITE_JPEG_QUALITY), 100]
        cv2.imwrite(os.path.join(pic_dir, str(batch).zfill(5) + str(xindex).zfill(3) + str(y).zfill(3) + ".png"), img,
                    [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

        np.save(os.path.join(npy_dir, str(batch).zfill(5) + str(xindex).zfill(3) + str(y).zfill(3)), matrix)
        with open(os.path.join(file_dir, str(batch).zfill(5) + str(xindex).zfill(3) + str(y).zfill(3) + ".txt"),
                  "w") as f:
            # f.write(str.format("numx:%d\tnumy:%d", numx, numy))
            for xy in lst_xy:
                for i in xy:
                    f.write(i)
                    f.write('\t')
                f.writelines('\n')


def meger_main(conf):
    os.makedirs(conf.get('merge_pic_path'), exist_ok=True)
    os.makedirs(conf.get('merge_npy_path'), exist_ok=True)
    os.makedirs(conf.get('merge_txt_path'), exist_ok=True)

    dir2file = check_file_name(conf.get('tiles_path'))
    numx = conf.get('x_tiles_nums')
    numy = conf.get('y_tiles_nums')
    sizew = conf.get('x_tile_size')
    sizeh = conf.get('y_tile_size')
    dest_dir = conf.get('merge_pic_path')
    file_dir = conf.get('merge_txt_path')
    npy_dir = conf.get('merge_npy_path')
    batch = conf.get('batch')
    merge_pic(dir2file, numx, numy, sizew, sizeh, dest_dir, file_dir, npy_dir, batch)


if __name__ == '__main__':
    # main(sys.argv[1:])
    print("start merge picture!")
    print("please wait for a sencond!")
    start = time.time()
    args = parse_argment()
    if args.file_dir is None:
        args.file_dir = args.dir_name + "/out/txt"
    if args.dest_dir is None:
        args.dest_dir = args.dir_name + "/out/pic"
    if args.npy_dir is None:
        args.npy_dir = args.dir_name + "/out/npy"
    dir2file = check_file_name(args.dir_name)
    os.makedirs(args.file_dir, exist_ok=True)
    os.makedirs(args.dest_dir, exist_ok=True)
    os.makedirs(args.npy_dir, exist_ok=True)
    merge_pic(dir2file, args.numx, args.numy, args.sizew, args.sizeh, args.dest_dir, args.file_dir, args.npy_dir,
              args.batch)
    end = time.time()
    print("need time is %f", end - start)
