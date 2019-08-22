import os
import os.path
import numpy as np
import xml.etree.ElementTree as xmlET

import pickle
from skimage import draw, data, io
from PIL import Image
#import matplotlib.pyplot as plt

if not os.path.exists('.\show_results'):
    os.mkdir('.\show_results')
txt_name = 'test_tree.txt'
file_path_img = '.\JPEGImages'
save_file_path = '.\show_results'

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



for idx,value in img_names.items():

    #img1 = io.imread(os.path.join(file_path_img, idx + '.jpg'))
    img = Image.open(os.path.join(file_path_img, idx + '.jpg'))
    img = np.array(img)

    for line in value:

        staff = line.split()

        box = staff
        rr,cc=draw.circle((int(np.round(float(box[1])))+int(np.round(float(box[3]))))/2,
                          (int(np.round(float(box[0])))+int(np.round(float(box[2]))))/2,10)

        img.flags.writeable = True

        draw.set_color(img,[rr, cc], color = [255,0,0])



    io.imsave(os.path.join(save_file_path, idx + '.jpg'),img)

