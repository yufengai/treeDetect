# /usr/bin/python
# --coding:utf8--
import argparse
import yaml
import img_merge_v2 as img_merge2
import img_merge
import infer
import tile2gps
import save_data_to_database
import logging
import pymysql
import time
import os


def parse_yaml(filename):
    with open(filename) as f:
        config = yaml.load(f)
    return config


def parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument('--yaml_path', help="config path", default='config.yaml')
    args1 = parse.parse_args()
    return args1


def get_cfg_from_database(cfg):
    db = pymysql.connect(
        host='47.97.155.10',
        port=3388,
        user='ai',
        password='VqMxFAyQ@123',
        db='data_warehouse',
        charset='utf8',
    )
    try:
        while True:
            cursor = db.cursor()
            cursor.execute('SELECT id , tiles_path FROM task WHERE status=2')
            db.commit()
            result = cursor.fetchall()
            if len(result) == 0:
                logging.info("*" * 50)
                logging.info('there is not have data change! sleep 60 seconds!')
                time.sleep(60)  # 睡眠60s
            else:
                break

    except Exception as e:
        logging.error("Wrong !", e)

    # TODO 现在只处理一条数据，后续有需要可以整改
    tiles_path = result[0][1]
    batch = result[0][0]
    cfg['tiles_path'] = tiles_path
    cfg['batch'] = batch
    return cfg


def change_database_status(status, batch):
    if status not in [3, 4]:
        logging.info('status is not 3 or 4')
    try:
        db = pymysql.connect(
            host='47.97.155.10',
            port=3388,
            user='ai',
            password='VqMxFAyQ@123',
            db='data_warehouse',
            charset='utf8',
        )
        cursor = db.cursor()
        # curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        update_sql = 'UPDATE task SET status = {} , updated_at = NOW() WHERE (id = {})'.format(status, batch)
        cursor.execute(update_sql)

        db.commit()

    except Exception as e:
        logging.error('update status error', e)
    finally:
        cursor.close()
        db.close()


def update_config(cfg):
    merge_pic_path = os.path.join(cfg.get('data_root'), str(cfg.get('batch')), cfg.get('merge_pic_path'))
    cfg['merge_pic_path'] = merge_pic_path

    merge_npy_path = os.path.join(cfg.get('data_root'), str(cfg.get('batch')), cfg.get('merge_npy_path'))
    cfg['merge_npy_path'] = merge_npy_path

    merge_txt_path = os.path.join(cfg.get('data_root'), str(cfg.get('batch')), cfg.get('merge_txt_path'))
    cfg['merge_txt_path'] = merge_txt_path

    result_txt_path = os.path.join(cfg.get('data_root'), str(cfg.get('batch')), cfg.get('result_txt_path'))
    cfg['result_txt_path'] = result_txt_path

    result_lat_lon_npy_path = os.path.join(cfg.get('data_root'), str(cfg.get('batch')),
                                           cfg.get('result_lat_lon_npy_path'))
    cfg['result_lat_lon_npy_path'] = result_lat_lon_npy_path

    result_lat_lon_txt_path = os.path.join(cfg.get('data_root'), str(cfg.get('batch')),
                                           cfg.get('result_lat_lon_txt_path'))
    cfg['result_lat_lon_txt_path'] = result_lat_lon_txt_path

    return cfg


if __name__ == '__main__':
    args = parse_args()
    conf = parse_yaml(args.yaml_path)
    print(conf.get('CUDA_VISIBLE_DEVICES'))

    while True:
        conf = get_cfg_from_database(conf)
        conf = update_config(conf)
        change_database_status(3, conf['batch'])
        # while loop
        logging.info('*' * 50)
        logging.info('doing merge tile to big picture! ')
        img_merge.meger_main(conf)

        logging.info('*' * 50)
        logging.info('doing infer')
        ret = infer.infer(conf)
        if ret != 0:
            logging.info('infer occour error')
            exit(-1)

        logging.info('*' * 50)
        logging.info('doing gen gps infomation!')
        tile2gps.gen_gps_npy(conf)

        logging.info('*' * 50)
        logging.info('save data to database!')
        save_data_to_database.save2database(conf)
        change_database_status(4, conf['batch'])
