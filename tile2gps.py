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
            default='test_tree.txt', type=str)
  parser.add_argument('--result_file_name',dest = 'file_name',help='lat and lon result file name',
            default='GPSData.txt', type=str)
  parser.add_argument('--npy_file_path',dest = 'npy_file_path',help='npy file path',
            default='.\\npy', type=str)


  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


  args = parser.parse_args()
  return args


#output every pixel deg in tile
def num2deg(xtile, ytile,xpixel,ypixel, zoom):
  n = 2.0 ** zoom
  lon_deg = (((xtile+(xpixel/256)) / (n) )* 360.0)- 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2* (ytile + (ypixel/256))/ n)))
  lat_deg = math.degrees(lat_rad)
  return lat_deg, lon_deg

#读取生成的检测文件
def split_txt(txt_name):
    source_file = open(txt_name)
    lines = source_file.readlines()
    img_names = {}
    for line in lines:
        staff = line.split()
        name = staff[0]
        conf = staff[1]
        x0 = staff[2]
        y0 = staff[3]
        x1 = staff[4]
        y1 = staff[5]
        if not name in img_names.keys():
            img_names[name] = [x0 + " " + y0 + " " + x1 + " " + y1]
        else:
            img_names[name].append(x0 + " " + y0 + " " + x1 + " " + y1)

    return img_names



def gen_gps(txt_name,zoom):
    img_names = split_txt(txt_name)
    list = []
    for idx,value in img_names.items():
        # gps_coord=[]

        for line in value:

            staff = line.split()
            box = staff[0:4]

            #每个框的大小W和H
            Wieth = int(np.round(float(box[3]))) - int(np.round(float(box[1])))
            Hight = int(np.round(float(box[2]))) - int(np.round(float(box[0])))

            # 取出每一个框的中心点坐标（x，y）
            xpixel = (int(np.round(float(box[1]))) + int(np.round(float(box[3]))))/2
            ypixel = (int(np.round(float(box[0]))) + int(np.round(float(box[2]))))/2

            # 像素点所在2048图片的位置在（x行y列）
            x = int(xpixel / 256)
            y = int(ypixel / 256)

            #相对于256图片的像素
            xpixel = xpixel - (x*256)
            ypixel = ypixel - (y*256)

            # 读取保存的瓦片编号文件的x行y列就是瓦片的编号
            #tile = np.load(idx +".npy")
            tile = np.load(os.path.join(args.npy_file_path, idx + ".npy"))
            tile_coord = tile[x][y]
            xtile = tile_coord[0]
            ytile = tile_coord[1]


            # 每个像素坐标转换成经纬度
            lat_deg, lon_deg = num2deg(xtile, ytile, xpixel, ypixel,zoom=21)
            lat_deg = abs(lat_deg)
            lon_deg = abs(lon_deg)

            list.append([xtile,ytile,zoom,lat_deg,lon_deg,Wieth,Hight])

            #np.save("list.npy",list)

    return list
            #写入txt
if __name__ == '__main__':
    args = parse_args()
    print('Called with args:')
    print(args)
    list = gen_gps(args.txt_name,21)
    with open(os.path.join(args.file_name), 'w') as f:
        for i in list:
            f.write('{} {} {}  {} {}    {} {}\n'.format(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))




