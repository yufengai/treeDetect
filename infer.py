#! /usr/local/python
# --coding:utf8--
import subprocess
import os
import logging
'''
usage: demo.py [-h] [--net {vgg16,res101}]
               [--dataset {pascal_voc,pascal_voc_0712}] [--vis]
               [--im_or_path IM_OR_PATH] [--out_result_path OUT_RESULT_PATH]
               [--tfmodel TFMODEL]

Tensorflow Faster R-CNN demo

optional arguments:
  -h, --help            show this help message and exit
  --net {vgg16,res101}  Network to use [vgg16 res101]
  --dataset {pascal_voc,pascal_voc_0712}
                        Trained dataset [pascal_voc pascal_voc]
  --vis                 is or not vis function
  --im_or_path IM_OR_PATH
                        one image or image path
  --out_result_path OUT_RESULT_PATH
                        out result file name
  --tfmodel TFMODEL     model path

'''


def infer(conf):
    # os.system('source /home/yufeng/test-faster-rcnn/test.sh')
    cmd_home = conf.get('faster_rcnn_cmd_path')
    gpu_id = conf.get('CUDA_VISIBLE_DEVICES')
    image_path = conf.get('merge_pic_path')
    net = conf.get('stonebone')
    weight_file = conf.get('weight_path')
    detect_out_txt = conf.get('result_txt_path')
    conda_env = conf.get('conda_env')
    conf_thresh = conf.get('conf_thresh')
    cmd_str = f'CUDA_VISIBLE_DEVICES={gpu_id} python {cmd_home}/tools/demo.py ' \
        f'--net {net} ' \
        f'--im_or_path {image_path} ' \
        f'--tfmodel {weight_file} ' \
        f'--out_result_path {detect_out_txt} ' \
        f'--conf_thresh {conf_thresh} '

    logging.info(cmd_str)
    errcode = os.system(cmd_str)
    print(errcode)

    return errcode


if __name__ == '__main__':
    infer(None)
