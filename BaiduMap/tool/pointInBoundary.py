import os
import time
import cx_Oracle
import threading
import pandas as pd


class LOGGER:
    def __init__(self):
        path = os.path.join(os.getcwd(), 'service.log')
        self.writer = open(path, mode='a')
        self.writer.write(self.get_suffix('INFO') + 'Logger created!\n')
        self.writer.flush()

    def get_suffix(self, type):
        suffix = ''
        suffix += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        suffix += ' - ' + type + ' - '
        return suffix

    def info(self, message):
        self.writer.write(self.get_suffix('INFO') + message + '\n')
        self.writer.flush()

    def error(self, message):
        self.writer.write(self.get_suffix('ERROR') + message + '\n')
        self.writer.flush()

    def close(self):
        self.writer.write(self.get_suffix('INFO') + 'Logger closed!')
        self.writer.flush()
        self.writer.close()


LOG = LOGGER()


def isRayIntersectsSegment(poi,s_poi,e_poi): #[x,y] [lng,lat]
    #输入：判断点，边起点，边终点，都是[lng,lat]格式数组
    if s_poi[1]==e_poi[1]: #排除与射线平行、重合，线段首尾端点重合的情况
        return False
    if s_poi[1]>poi[1] and e_poi[1]>poi[1]: #线段在射线上边
        return False
    if s_poi[1]<poi[1] and e_poi[1]<poi[1]: #线段在射线下边
        return False
    if s_poi[1]==poi[1] and e_poi[1]>poi[1]: #交点为下端点，对应spoint
        return False
    if e_poi[1]==poi[1] and s_poi[1]>poi[1]: #交点为下端点，对应epoint
        return False
    if s_poi[0]<poi[0] and e_poi[1]<poi[1]: #线段在射线左边
        return False

    xseg=e_poi[0]-(e_poi[0]-s_poi[0])*(e_poi[1]-poi[1])/(e_poi[1]-s_poi[1]) #求交
    if xseg<poi[0]: #交点在射线起点的左侧
        return False
    return True  #排除上述情况之后


def isPoiWithinPoly(poi,poly):
    #输入：点，多边形三维数组
    #poly=[[[x1,y1],[x2,y2],……,[xn,yn],[x1,y1]],[[w1,t1],……[wk,tk]]] 三维数组

    #可以先判断点是否在外包矩形内
    #if not isPoiWithinBox(poi,mbr=[[0,0],[180,90]]): return False
    #但算最小外包矩形本身需要循环边，会造成开销，本处略去
    sinsc=0 #交点个数
    for epoly in poly: #循环每条边的曲线->each polygon 是二维数组[[x1,y1],…[xn,yn]]
        for i in range(len(epoly)-1): #[0,len-1]
            s_poi=epoly[i]
            e_poi=epoly[i+1]
            if isRayIntersectsSegment(poi,s_poi,e_poi):
                sinsc+=1 #有交点就加1

    return True if sinsc%2==1 else  False


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


def process_thread(points_array, boundary):
    for row in boundary:
        path_id = str(row[0])
        path_list = str(row[1]).split(";")
        # 将 path_list 构造成poly
        poly = []
        for i in range(len(path_list) - 1):
            point1 = [float(path_list[i].split(',')[0]),
                      float(path_list[i].split(',')[1])]
            point2 = [float(path_list[i + 1].split(',')[0]),
                      float(path_list[i + 1].split(',')[1])]
            poly.append([point1, point2])

        in_boundary_point = []
        for point in points_array:
            if isPoiWithinPoly(point, poly):
                in_boundary_point.append(str(point[0]) + ',' + str(point[1]))

        db = cx_Oracle.connect('geminit', 'hack', '192.168.0.112:1521/helowin')
        cr = db.cursor()
        cr.setinputsizes(POINTS=cx_Oracle.CLOB)
        cr.execute("insert into REACHABLE_POINT (ID, POINTS) values ('" + path_id + "', :POINTS)", POINTS=';'.join(in_boundary_point))
        cr.close()
        db.commit()
        db.close()

        LOG.info(str(path_id) + ' reachable_point size: ' + str(len(in_boundary_point)))


if __name__ == '__main__':
    db = cx_Oracle.connect('geminit', 'hack', '192.168.0.112:1521/helowin')
    cr = db.cursor()
    cr.execute("select * from MAP_POINT")
    rs = cr.fetchall()
    columns = [i[0] for i in cr.description]
    all_point = pd.DataFrame(rs, columns=columns)[['ID', 'LNG', 'LAT', 'TYPE']]
    cr = db.cursor()
    cr.execute("select ID, PATH from BOUNDARY order by ID asc")
    boundary = []
    for i in cr:
        text = i[1].read()
        boundary.append([i[0], text])
    cr.close()
    db.close()

    points_array = []
    for row in all_point.itertuples():
        points_array.append([float(row.LNG), float(row.LAT)])

    boundary_part = divide_list_to_parts(boundary, 5)

    thread_list = []
    for i in range(len(boundary_part)):
        thread_list.append(
            threading.Thread(target=process_thread, args=(points_array, boundary_part[i])))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
