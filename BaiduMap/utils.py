# -*- coding: utf-8 -*-
import conf
import json
import time
import requests
import cx_Oracle
import traceback
import pandas as pd
from logger import LOG


def http_get(url, params, type):
    """
    http的get方法
    :param url
    :param params
    :param type
    :return: results
    """
    key = conf.HTTP_RESPONSE_KEY[type]
    # 3次重试
    for i in range(3):
        params['ak'] = conf.AK[conf.AK_INDEX]
        # 防止并发过大，导致请求失败，每次请求后都挂起0.05秒
        time.sleep(0.05)
        try:
            response = json.loads(requests.get(url, params=params).content)
        except:
            message = '发送HTTP请求时发生错误。'
            e = traceback.format_exc()
            if e is not None:
                message += '错误详情：' + e
            response = {'status': 401, 'message': message}
        if type == 'BOUNDARY' or response['status'] == 0:
            return response[key]
        elif i == 2:
            error_message = "根据URL：" + url + "获取失败， params:" + str(params)
            if 'message' in response:
                error_message += '. \nmessage: ' + str(response['message'])
            LOG.error(error_message)
    return []


def get_points_from_oracle():
    """
    从数据库获取小区点和资源点
    :return: all_point: 所有点，包括小区点和资源点。结构：pandas.dataframe
    """
    db = cx_Oracle.connect(conf.ORACLE_NAME, conf.ORACLE_PASSWORD, conf.ORACLE_URL)
    cr = db.cursor()
    cr.execute("select * from MAP_POINT order by ID asc")
    rs = cr.fetchall()
    columns = [i[0] for i in cr.description]
    all_point = pd.DataFrame(rs, columns=columns)[['ID', 'LNG', 'LAT', 'TYPE']]
    cr.close()
    db.close()

    return all_point


def write_boundary_and_reachable_point_into_oracle(ID, boundary, reachable_point):
    """
    按照ID，将边界和可达点存到数据库中
    :param ID: MAP_POINT表中的ID
    :param boundary: 边界list
    :param reachable_point: 可达点list
    """
    db = cx_Oracle.connect(conf.ORACLE_NAME, conf.ORACLE_PASSWORD, conf.ORACLE_URL)

    exist_in_boundary = False
    exist_in_reachable_point = False

    cr = db.cursor()
    cr.execute("select * from BOUNDARY where ID='" + ID + "'")
    rs = cr.fetchall()
    if len(rs) > 0:
        exist_in_boundary = True
    cr.close()

    cr = db.cursor()
    cr.execute("select * from REACHABLE_POINT where ID='" + ID + "'")
    rs = cr.fetchall()
    if len(rs) > 0:
        exist_in_reachable_point = True
    cr.close()

    cr = db.cursor()
    if exist_in_boundary:
        cr.setinputsizes(PATH=cx_Oracle.CLOB)
        cr.execute("update BOUNDARY set PATH=:PATH where ID='" + ID + "'",
                   PATH=';'.join(boundary))
    else:
        cr.setinputsizes(PATH=cx_Oracle.CLOB)
        cr.execute("insert into BOUNDARY (ID, PATH) values ('" + ID + "', :PATH)",
                   PATH=';'.join(boundary))
    cr.close()

    cr = db.cursor()
    if exist_in_reachable_point:
        cr.setinputsizes(POINTS=cx_Oracle.CLOB)
        cr.execute("update REACHABLE_POINT set POINTS=:POINTS where ID='" + ID + "'",
                   POINTS=';'.join(reachable_point))
    else:
        cr.setinputsizes(POINTS=cx_Oracle.CLOB)
        cr.execute("insert into REACHABLE_POINT (ID, POINTS) values ('" + ID + "', :POINTS)",
                   POINTS=';'.join(reachable_point))
    cr.close()

    db.commit()
    db.close()


def divide_list_to_parts(list, n):
    """
    将一个list尽可能平均分成n份
    :param list: 原list
    :param n: 分成几个list
    :param list_parts 结果
    """
    list_parts = [[] for i in range(n)]
    for i, e in enumerate(list):
        list_parts[i % n].append(e)
    return list_parts
