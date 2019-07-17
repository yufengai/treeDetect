import numpy as np
import pymysql
import datetime
import sys, getopt


def data_to_list(data_dir):
    data = np.load(data_dir)
    data_list = [[0 for a in range(9)] for b in range(len(data))]
    db = pymysql.connect(
        host='120.79.71.187',
        port=3388,
        user='ai',
        password='Yfzn@123',
        db='data_warehouse',
        charset='utf8',
    )
    cursor = db.cursor()
    cursor.execute('SELECT orchard_id FROM tree_location ORDER BY tree_id DESC LIMIT 1')
    db.commit()
    last_orchard_id = cursor.fetchall()
    if last_orchard_id:
        last_orchard_id = last_orchard_id[0][0]
        last_orchard_id += 1
    else:
        last_orchard_id = 1
    cursor.close()
    db.close()
    for i in range(len(data)):
        data_list[i][0] = last_orchard_id
        data_list[i][1: 8] = data[i]
        data_list[i][8] = str(datetime.datetime.now())
        for j in range(3):
            data_list[i][j + 1] = int(data_list[i][j + 1])
        for k in range(4):
            data_list[i][k + 4] = float(data_list[i][k + 4])
    return data_list


def insert_data(data_list):
    db = pymysql.connect(
        host='120.79.71.187',
        port=3388,
        user='ai',
        password='Yfzn@123',
        db='data_warehouse',
        charset='utf8',
    )
    cursor = db.cursor()
    sql_str = 'INSERT INTO tree_location (orchard_id, tile_x, tile_y, tile_z, longitude,' \
              ' latitude, length, width, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) '

    try:
        cursor.executemany(sql_str, data_list)
        db.commit()
    except:
        print("Wrong! Do rollback!")
        db.rollback()
    cursor.close()
    db.close()


def main(argv):
    dir = ''
    try:
        opts, args = getopt.getopt(argv, "hd:", ["dir_name=", ])
    except getopt.GetoptError:
        print('save_data_to_database.py -d <dir_name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('save_data_to_database.py -d <dir_name>')
            print('Input_Example: python save_data_to_database.py -d "data.npy"')
            sys.exit()
        elif opt in ("-d", "--dir_name"):
            dir = arg

    data_list = data_to_list(dir)
    insert_data(data_list)


if __name__ == '__main__':
    main(sys.argv[1:])
