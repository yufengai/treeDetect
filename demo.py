#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths
from model.config import cfg
from model.test import im_detect
from model.nms_wrapper import nms

from utils.timer import Timer
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os, cv2
import argparse

from nets.vgg16 import vgg16
from nets.resnet_v1 import resnetv1

CLASSES = ('__background__',
           'tree')

NETS = {'vgg16': ('vgg16_faster_rcnn_iter_20000.ckpt',), 'res101': ('res101_faster_rcnn_iter_190000.ckpt',)}
DATASETS = {'pascal_voc': ('voc_2007_trainval',), 'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}


def vis_detections(image_name, im, class_name, dets, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=2)
        )
        # ax.text(bbox[0], bbox[1] - 2,
        #         '{:s} {:.3f}'.format(class_name, score),
        #         bbox=dict(facecolor='blue', alpha=0.5),
        #         fontsize=14, color='white')

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                 fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()

    ##
    plt.savefig('/tmp/infer_demo/' + os.path.split(image_name)[-1])
    print("/tmp/infer_demo/{}".format(os.path.split(image_name)[-1]))


def demo(image_name, sess, net, vis, CONF_THRESH=0.8):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    # im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(image_name)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class

    NMS_THRESH = 0.3

    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1  # because we skipped background
        cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        dets = dets[np.where(dets[:, -1] >= float(CONF_THRESH))]

        if vis:
            vis_detections(image_name, im, cls, dets, thresh=float(CONF_THRESH))
    return dets


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='res101')
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc]',
                        choices=DATASETS.keys(), default='pascal_voc')
    parser.add_argument('--vis', action='store_true', help='is or not vis function')
    parser.add_argument('--im_or_path', default='/home/data/tree/tile/0722/out/pic/', help='one image or image path')
    # im_or_path = data/demo
    parser.add_argument('--out_result_path', default='/tmp/tree.txt', help='out result file name')
    parser.add_argument('--conf_thresh', default=0.1, help='confident thresh')
    parser.add_argument('--tfmodel',
                        default='output/res101/voc_2007_trainval/default/res101_faster_rcnn_iter_190000.ckpt',
                        help='model path')
    args = parser.parse_args()

    return args


def save_result(detDict, out_path):
    with open(out_path, 'w') as f:
        for name, dets in detDict.items():
            name = os.path.splitext(name)[0]
            for det in dets:
                ss = '{}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.4f}\n'.format(name, det[-1], det[0], det[1], det[2],
                                                                           det[3])
                # print(ss)
                f.write(ss)
            f.flush()


if __name__ == '__main__':

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    args = parse_args()
    # os.putenv("CUDA_VISIBLE_DEVICES", '1')
    print(args)
    # model path
    demonet = args.demo_net
    dataset = args.dataset
    tfmodel = args.tfmodel
    # tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default', NETS[demonet][0])

    if not os.path.isfile(tfmodel + '.meta'):
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    print(tfmodel)
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth = True

    # init session
    sess = tf.Session(config=tfconfig)
    # load network
    if demonet == 'vgg16':
        net = vgg16()
    elif demonet == 'res101':
        net = resnetv1(num_layers=101)
    else:
        raise NotImplementedError
    net.create_architecture("TEST", 2,
                            tag='default', anchor_scales=[0.5, 1, 2, 3], anchor_ratios=[0.5, 1, 2])
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))

    # im_names = ['000003.jpg', '000004.jpg', '000018.jpg', '000020.jpg',
    #             '000039.jpg', '000041.jpg', '000060.jpg', '000065.jpg']
    im_names = os.listdir(args.im_or_path)
    # map(mapfun,im_names)
    detdict = {}
    for im_name in im_names:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        im_name_path = os.path.join(args.im_or_path, im_name)
        print('Demo for {}'.format(im_name_path))
        dets = demo(im_name_path, sess, net, args.vis, args.conf_thresh)
        detdict[im_name] = dets
    save_result(detdict, args.out_result_path)
    # plt.show()
