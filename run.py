# /usr/bin/python
# --coding:utf8--
import argparse
import yaml
import img_merge
import infer
import tile2gps
import save_data_to_database


def parse_yaml(filename):
    with open(filename) as f:
        conf = yaml.load(f)
    return conf


def parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument('--yaml_path', help="config path", default='config.yaml')
    args = parse.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    conf = parse_yaml(args.yaml_path)
    print(conf.get('CUDA_VISIBLE_DEVICES'))
    img_merge.meger_main(conf)

    infer.infer(conf)

    tile2gps.gen_gps_npy(conf)
    save_data_to_database.save2database(conf)



