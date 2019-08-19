# coding:utf-8
import numpy as np
import math
import os
import argparse
import sys

def parse_args():
  """
  Parse input arguments
  """
  parser = argparse.ArgumentParser(description='Transfor a Latitude and longitude coordinates')

  parser.add_argument('--txt_dir',dest = 'txt_name',help='detectron result txt file name',
            default='/home/data/merged/724/test_tree.txt', type=str)
  parser.add_argument('--result_file_name', dest='file_name', help='lat and lon result file name',
                      default='/home/data/merged/724/GPSData.txt', type=str)
  parser.add_argument('--out_npy', dest='out_npy', help='lat and lon result file name',
                      default='/home/data/merged/724/list.npy', type=str)
  parser.add_argument('--npy_file_path', dest='npy_file_path', help='merger pic gen npy file path',
            default='/home/data/merged/724/npy/', type=str)


  # if len(sys.argv) == 1:
  #   parser.print_help()
  #   sys.exit(1)


  args = parser.parse_args()
  return args



def num2deg(xtile, ytile,xpixel,ypixel, zoom):
    """
    #output every pixel deg in tile
    :param xtile:
    :param ytile:
    :param xpixel:
    :param ypixel:
    :param zoom:
    :return:
    """
    n = 2.0 ** zoom
    # 经度
    lon_deg = (((xtile+(xpixel/256)) / (n) )* 360.0) - 180.0
    # 纬度
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2* (ytile + (ypixel/256))/ n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def split_txt(txt_name):
    """
    #读取生成的检测文件
    :param txt_name:
    :return:
    """
    source_file = open(txt_name)
    lines = source_file.readlines()
    img_names = {}
    for line in lines:
        staff = line.split()
        # 照片名称
        name = staff[0]
        # 置信度
        conf = staff[1]
        # point1 点位置
        x0 = staff[2]
        y0 = staff[3]
        # point2的点位置
        x1 = staff[4]
        y1 = staff[5]
        if not name in img_names.keys():
            img_names[name] = [x0 + " " + y0 + " " + x1 + " " + y1]
        else:
            img_names[name].append(x0 + " " + y0 + " " + x1 + " " + y1)

    return img_names


def gen_gps(txt_name, zoom):
    """

    :param txt_name:
    :param zoom:
    :return:
    """
    img_names = split_txt(txt_name)
    list = []
    tmpsetx = set()
    tmpsety = set()
    # idx是照片名称，value是idx下所有的点列表
    for idx, value in img_names.items():
        # gps_coord=[]

        for line in value:

            # staff = line.split()
            box = line.split()
            # box = staff[0:4]

            #每个框的大小W和H
            Wieth = int(np.round(float(box[3]))) - int(np.round(float(box[1])))
            Hight = int(np.round(float(box[2]))) - int(np.round(float(box[0])))

            # 取出每一个框的中心点坐标（x，y）
            xpixel = (int(np.round(float(box[0]))) + int(np.round(float(box[2])))) / 2
            ypixel = (int(np.round(float(box[1]))) + int(np.round(float(box[3]))))/2

            # 像素点所在2048图片的位置在（x行y列）
            x = int(xpixel / 256)
            y = int(ypixel / 256)

            #相对于256图片的像素

            xpixel = xpixel - (x*256)
            ypixel = ypixel - (y*256)
            ypixel = 256 - ypixel

            # 读取保存的瓦片编号文件的x行y列就是瓦片的编号
            # if idx != "000004":
            #     continue
            tile = np.load(os.path.join(args.npy_file_path, idx + ".npy"))
            tile_coord = tile[y][x]
            xtile = tile_coord[0]
            ytile = tile_coord[1]


            # 每个像素坐标转换成经纬度
            lat_deg, lon_deg = num2deg(xtile, ytile, xpixel, ypixel, zoom=21)
            lat_deg = abs(lat_deg)
            lon_deg = abs(lon_deg)

            list.append([xtile, ytile, zoom, lon_deg, lat_deg, Wieth, Hight])

            # np.save("list.npy", list)

    return list
            #写入txt


def _tiletogps():
    lst = []
    for idx in range(1, 91):
        tile = np.load(os.path.join(args.npy_file_path, str(idx).zfill(6) + ".npy"))
        for x in range(8):
            for y in range(8):
                tile_coord = tile[x][y]
                xtile = tile_coord[0]
                ytile = tile_coord[1]
                lat_deg, lon_deg = num2deg(xtile, ytile, 0, 0, zoom=21)
                lst.append([xtile, ytile, 21, abs(lat_deg), abs(lon_deg), 0, 0])
    return lst


def gen_gps_npy(conf):
    lst = gen_gps(conf.get('result_txt_path'), conf.get('z_tile'))
    np.save(conf.get('result_lat_lon_npy_path'), lst)


if __name__ == '__main__':
    args = parse_args()
    print('Called with args:')
    print(args)
    lst = gen_gps(args.txt_name, 21)
    # lst = tiletogps()
    with open(os.path.join(args.file_name), 'w') as f:
        for i in lst:
            f.write('{} {} {}  {} {}    {} {}\n'.format(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
    np.save(args.out_npy, lst)
    # tmp = num2deg(859267, 601480, 0, 0, 20)
    # print(tmp)

    print("----------------")


