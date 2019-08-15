import numpy as np
import pymysql
import datetime
import time
import sys, getopt
import logging
# 单例模式
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(filename)s %(funcName)s  %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d  %H:%M:%S %a'    #注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    )
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def data_to_list(data_dir):
    data = np.load(data_dir)
    data_list = [[0 for a in range(10)] for b in range(len(data))]
    db = pymysql.connect(
        host='47.97.155.10 ',
        port=3388,
        user='ai',
        password='VqMxFAyQ@123',
        db='data_warehouse',
        charset='utf8',
    )
    try:
        cursor = db.cursor()
        cursor.execute('SELECT batch_id FROM tree_location group by batch_id ORDER BY batch_id DESC LIMIT 1')
        db.commit()
        last_batch_id = cursor.fetchall()
        if last_batch_id:
            last_batch_id = last_batch_id[0][0]
            last_batch_id = int(last_batch_id) + 1
        else:
            last_batch_id = 1
    except Exception as e:
        logger.error("Wrong !", e)
    finally:
        cursor.close()
        db.close()
    # print(last_batch_id)
    # last_batch_id = 0
    curr_time = str(datetime.datetime.now())
    # curr_time = str('2019-08-15 09:03:30')
    # print(curr_time)
    for i in range(len(data)):
        data_list[i][0] = last_batch_id
        data_list[i][1: 8] = data[i]
        data_list[i][8] = curr_time
        # data_list[i][8] = str(1)
        data_list[i][9] = 0
        for j in range(3):
            data_list[i][j + 1] = int(data_list[i][j + 1])
        for k in range(4):
            data_list[i][k + 4] = float(data_list[i][k + 4])
    for i,d in enumerate(data_list):
        data_list[i] = tuple(d)

    return data_list, last_batch_id


def insert_data(data_list, last_batch_id):
    db = pymysql.connect(
        host='47.97.155.10',
        port=3388,
        user='ai',
        password='VqMxFAyQ@123',
        db='data_warehouse',
        charset='utf8',
    )
    cursor = db.cursor()
    sql_str = 'INSERT INTO tree_location (' \
              '`batch_id`   , ' \
              '`tile_x`     , ' \
              '`tile_y`     , ' \
              '`tile_z`     , ' \
              '`longitude`  , ' \
              '`latitude`   , ' \
              '`length`     , ' \
              '`width`      , ' \
              '`create_time`, ' \
              '`from`       )'\
              'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s )'

    try:

        # print(len(data_list))
        logger.info("do insert batch data in id:= %s", last_batch_id)
        cursor.executemany(sql_str, data_list)
        db.commit()
        logger.info("do update batch data in id:= %s", last_batch_id)
        sql_update = "update tree_location set tree_point = st_GeomFromText(CONCAT('POINT(',longitude,' ',latitude,')'))  " \
                     "where batch_id=" + str(last_batch_id)
        cursor.execute(sql_update)
        db.commit()



    except Exception as e:
        logger.error("Wrong! Do rollback!", e)
        db.rollback()
    finally:
        cursor.close()
        db.close()


def main(argv):
    dir = '/home/data/tree/merged/724/list.npy'
    # try:
    #     opts, args = getopt.getopt(argv, "hd:", ["dir_name=", ])
    # except getopt.GetoptError:
    #     print('save_data_to_database.py -d <dir_name>')
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt == '-h':
    #         print('save_data_to_database.py -d <dir_name>')
    #         print('Input_Example: python save_data_to_database.py -d "data.npy"')
    #         sys.exit()
    #     elif opt in ("-d", "--dir_name"):
    #         dir = arg

    data_list, batch_id = data_to_list(dir)
    insert_data(data_list, batch_id)


if __name__ == '__main__':
    main(sys.argv[1:])
