# -*- coding: utf-8 -*-
import re
import pymysql
import cx_Oracle
import pandas as pd


if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', user='root', passwd='hack', db='bdmap', charset='utf8mb4')
    cursor = conn.cursor()

    sql = 'insert into MAP_POINT values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    dns_tns = cx_Oracle.makedsn('192.168.0.110', '1521', sid='ORCL')
    db = cx_Oracle.connect('sys', 'sys', dns_tns, cx_Oracle.SYSDBA)
    cr = db.cursor()
    cr.execute("select * from DEMO.MAP_POINT order by ID asc")
    rs = cr.fetchall()
    columns = [i[0] for i in cr.description]
    all_point = pd.DataFrame(rs, columns=columns)
    cr.close()
    db.close()
    for row in all_point.itertuples():
        cursor.execute(sql, (row.ID, row.NAME, row.STREET_ID, row.LNG, row.LAT, row.ADDRESS, row.PROVINCE, row.CITY,
                             row.AREA, row.NAVI_LNG, row.NAVI_LAT, row.TAG, row.TYPE, row.OVERALL_RATING,
                             row.COMMENT_NUM, row.CONTENT_TAG, row.QSC_POINT_TYPE))

    sql = 'insert into BOUNDARY values(%s, %s)'
    file = open("./BOUNDARY.sql")
    for line in file.readlines():
        line = line.strip()
        m = re.match(".*?\'(.*?)\', \'(.*?)\'.*", line)
        id = m.group(1)
        boundary = m.group(2)
        cursor.execute(sql, (id, boundary))

    sql = 'insert into REACHABLE_POINT values(%s, %s)'
    file = open("./REACHABLE_POINT.sql")
    for line in file.readlines():
        line = line.strip()
        m = re.match(".*?\'(.*?)\', \'(.*?)\'.*", line)
        if m:
            id = m.group(1)
            points = m.group(2)
            cursor.execute(sql, (id, points))
        else:
            m = re.match(".*?\'(.*?)\', null.*", line)
            id = m.group(1)
            cursor.execute(sql, (id, ''))

    cursor.close()
    conn.commit()
    conn.close()
    print('sql执行成功')
