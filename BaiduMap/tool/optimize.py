import math
import pymysql


def optimize_path(boundary_path_list):
    """
    优化现有的边界点数组
    :param: boundary_path_list 边界点顺序集合  如：
    ['39.915,116.404'， '39.915,116.404'， '39.915,116.404'， '39.915,116.404']
    :return: boundary_path_list 边界点顺序集合  如：
    ['39.915,116.404'， '39.915,116.404'， '39.915,116.404']
    """
    #
    # 首先，boundary_path_list 中存在重复点的情况，现用以下算法去除重复部分
    #

    # 构造一个map对象，用于存放 boundary_path_list 中每一个点的index列表
    point_indexes_map = {}
    # 构造一个set对象，用于存放 boundary_path_list 中所有重复的点
    point_map_duplicate_keys = set()
    # 遍历 boundary_path_list，填满上方构造的两个变量
    for i in range(0, len(boundary_path_list)):
        if boundary_path_list[i] in point_indexes_map:
            point_map_duplicate_keys.add(boundary_path_list[i])
            point_indexes_map[boundary_path_list[i]].append(i)
        else:
            point_indexes_map[boundary_path_list[i]] = [i]

    # 构造一个set对象，用于存放 boundary_path_list 中所有需要删除的index列表
    to_be_deleted_indexes = set()
    # 遍历 point_map_duplicate_keys，得到所有需要删除的indexes，放入 to_be_deleted_indexes
    for key in point_map_duplicate_keys:
        # 根据重复点，从 point_indexes_map 中获取该点所有的index，并排序
        point_map_duplicate_indexes = point_indexes_map[key]
        point_map_duplicate_indexes.sort()
        # 计算该点所有不同index之间的距离
        indexes_lengths = []
        for i in range(0, len(point_map_duplicate_indexes)):
            if i + 1 < len(point_map_duplicate_indexes):
                indexes_lengths.append(point_map_duplicate_indexes[i + 1] - point_map_duplicate_indexes[i])
            else:
                indexes_lengths.append(point_map_duplicate_indexes[0] +
                                       len(boundary_path_list) - point_map_duplicate_indexes[i])
        # 不同index的点作为left_index时，left_index到right_index的总长度
        index_total_lengths = []
        for i in range(0, len(indexes_lengths)):
            total_length = 0
            for j in range(0, len(indexes_lengths) - 1):
                k = i + j
                if k >= len(indexes_lengths):
                    k = k % len(indexes_lengths)
                total_length += indexes_lengths[k]
            index_total_lengths.append(total_length)
        # 得到 left_index 到 right_index 的总长度最短时的 left_index 和 right_index
        left_index = point_map_duplicate_indexes[index_total_lengths.index(min(index_total_lengths))]
        right_index = point_map_duplicate_indexes[index_total_lengths.index(min(index_total_lengths)) - 1]
        # 最后根据 left_index 和 right_index 得到该点需要删除的所有indexes
        if left_index < right_index:
            for i in range(left_index, right_index):
                to_be_deleted_indexes.add(i)
        else:
            for i in range(0, right_index):
                to_be_deleted_indexes.add(i)
            for i in range(left_index, len(boundary_path_list)):
                to_be_deleted_indexes.add(i)

    # 将 to_be_deleted_indexes 转成list并排序、反转，最后得到没有重复点的 boundary_path_list
    to_be_deleted_indexes_list = list(to_be_deleted_indexes)
    to_be_deleted_indexes_list.sort()
    to_be_deleted_indexes_list.reverse()
    for index in to_be_deleted_indexes_list:
        del boundary_path_list[index]

    # 将 boundary_path_list 首尾相连
    if len(boundary_path_list) > 0 and not boundary_path_list[0] == boundary_path_list[len(boundary_path_list) - 1]:
        boundary_path_list.append(boundary_path_list[0])

    #
    # 此时的 boundary_path_list 已经没有重复点了，但是还存在细长条的不美观现象，现利用以下算法进行优化
    #

    # 优化条件为 boundary_path_list 长度大于四，即至少需要三个不用点
    if len(boundary_path_list) < 4:
        return boundary_path_list

    # 构造一个map对象，用于存储 boundary_path_list 中每个点到其他点的距离
    point_point_length_map = {}
    # 遍历 boundary_path_list， 填满上方构造的 boundary_path_list
    for i in range(0, len(boundary_path_list) - 1):
        point1 = boundary_path_list[i]
        for j in range(i + 1, len(boundary_path_list)):
            point2 = boundary_path_list[j]
            point1_x = float(point1.split(',')[0])
            point1_y = float(point1.split(',')[1])
            point2_x = float(point2.split(',')[0])
            point2_y = float(point2.split(',')[1])
            length = math.sqrt(math.pow(point2_y - point1_y, 2) + math.pow(point2_x - point1_x, 2))
            if not point1 in point_point_length_map:
                point_point_length_map[point1] = {}
            if not point2 in point_point_length_map:
                point_point_length_map[point2] = {}
            point_point_length_map[point1][point2] = length
            point_point_length_map[point2][point1] = length

    # 构造一个set对象，用于存放 boundary_path_list 中所有需要删除的indexes
    to_be_deleted_indexes = set()
    # 遍历 boundary_path_list 中所有点，即 point_point_length_map 中所有点
    # 算法思想是，如果一个点，距其最近的两个点不是它的上一个点和下一个点，则将最近两个点之间的点全部删除
    for point in point_point_length_map:
        # 从 point_point_length_map 中获取当前点到其他所有点的距离map对象
        to_point_length = point_point_length_map[point]
        # 获取距离当前点最近的两个点
        sorted_point_length_list = sorted(to_point_length.items(), key=lambda x:x[1], reverse=False)
        first_near_point = sorted_point_length_list[0][0]
        first_near_length = sorted_point_length_list[0][1]
        second_near_point = sorted_point_length_list[1][0]
        second_near_length = sorted_point_length_list[1][1]
        # 获取当前点的index
        point_index = boundary_path_list.index(point)

        if first_near_length > 0.0009 or second_near_length > 0.0009:
            continue

        # 构造一个list对象，用于存储距离当前点最近的两个点的index
        nearest_two_point_index = []
        if boundary_path_list[point_index - 1] == first_near_point and \
                boundary_path_list[point_index + 1] == second_near_point:
            # 如果最近的点是当前点的上一个点并且第二近的点是当前点的下一个点，则跳过此次循环，不删除任何点
            continue
        elif boundary_path_list[point_index - 1] == second_near_point and \
                boundary_path_list[point_index + 1] == first_near_point:
            # 如果最近的点是当前点的下一个点并且第二近的点是当前点的上一个点，则跳过此次循环，不删除任何点
            continue
        elif boundary_path_list[point_index - 1] == first_near_point or \
                boundary_path_list[point_index - 1] == second_near_point:
            # 如果当前点的上一个点是最近点或者第二近点，而当前点的下一个点不是，则记录当前点最近的两个点的index
            nearest_two_point_index.append(boundary_path_list.index(first_near_point))
            nearest_two_point_index.append(boundary_path_list.index(second_near_point))
        elif boundary_path_list[point_index + 1] == second_near_point or \
                boundary_path_list[point_index + 1] == second_near_point:
            # 如果当前点的下一个点是最近点或者第二近点，而当前点的上一个点不是，则记录当前点最近的两个点的index
            nearest_two_point_index.append(boundary_path_list.index(first_near_point))
            nearest_two_point_index.append(boundary_path_list.index(second_near_point))
        else:
            # 如果当前点的上一个点和下一个点都不是最近点或者第二近点，则记录当前点最近的两个点的index
            nearest_two_point_index.append(boundary_path_list.index(first_near_point))
            nearest_two_point_index.append(boundary_path_list.index(second_near_point))
        # 计算出当前点最近两个点之间的距离
        tow_indexes_between = math.fabs(nearest_two_point_index[0] - nearest_two_point_index[1])
        # 删除两点间距离短的那一边，将其中所有indexes放入 to_be_deleted_indexes
        if len(boundary_path_list) / 2 > tow_indexes_between:
            for i in range(min(nearest_two_point_index) + 1, max(nearest_two_point_index)):
                to_be_deleted_indexes.add(i)
        else:
            for i in range(0, min(nearest_two_point_index)):
                to_be_deleted_indexes.add(i)
            for i in range(max(nearest_two_point_index) + 1, len(boundary_path_list)):
                to_be_deleted_indexes.add(i)

    # 将 to_be_deleted_indexes 转成list并排序、反转，最后得到没有不美观的细长条的 boundary_path_list
    to_be_deleted_indexes_list = list(to_be_deleted_indexes)
    to_be_deleted_indexes_list.sort()
    to_be_deleted_indexes_list.reverse()
    for index in to_be_deleted_indexes_list:
        del boundary_path_list[index]

    # 将 boundary_path_list 首尾相连
    if len(boundary_path_list) > 0 and not boundary_path_list[0] == boundary_path_list[len(boundary_path_list) - 1]:
        boundary_path_list.append(boundary_path_list[0])

    return boundary_path_list


def is_ray_intersects_segment(poi, s_poi, e_poi):
    """
    判断射线是否相交
    :param poi: 目标点， 如 [39.915,116.404]
    :param s_poi: 边的一个顶点， 如 [39.915,116.404]
    :param e_poi: 边的另一个顶点， 如 [39.915,116.404]
    :return: True/False 是否相交
    """
    if s_poi[1] == e_poi[1]:
        # 排除与射线平行、重合，线段首尾端点重合的情况
        return False
    if s_poi[1] > poi[1] and e_poi[1] > poi[1]:
        # 线段在射线上边
        return False
    if s_poi[1] < poi[1] and e_poi[1] < poi[1]:
        # 线段在射线下边
        return False
    if s_poi[1] == poi[1] and e_poi[1] > poi[1]:
        # 交点为下端点，对应spoint
        return False
    if e_poi[1] == poi[1] and s_poi[1] > poi[1]:
        # 交点为下端点，对应epoint
        return False
    if s_poi[0] < poi[0] and e_poi[1] < poi[1]:
        # 线段在射线左边
        return False
    # 求交
    xseg = e_poi[0] - (e_poi[0] - s_poi[0]) * (e_poi[1] - poi[1]) / (e_poi[1] - s_poi[1])
    if xseg < poi[0]:
        # 交点在射线起点的左侧
        return False
    # 排除上述情况之后
    return True


def is_poi_within_poly(poi, poly):
    """
    判断某个点是否在一个多边形内部
    :param poi: 目标点， 如 [39.915,116.404]
    :param poly: 多边形的三维数组，第二维是多边形的边，第三维是边的两个顶点
    如 [[[39.915,116.404], [39.915,116.404]], [[39.915,116.404], [39.915,116.404]], [[39.915,116.404], [39.915,116.404]]]
    :return: True/False 是否相交
    """
    # 交点个数
    intersection = 0
    # 循环每条边的曲线->each polygon 是二维数组[[x1,y1],[x2,y2]]
    for epoly in poly:
        if is_ray_intersects_segment(poi, epoly[0], epoly[1]):
            # 有交点 sinsc 就加1
            intersection += 1
    return True if intersection % 2 == 1 else False


if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', user='root', passwd='hack', db='bdmap', charset='utf8mb4')
    cursor = conn.cursor()

    sql = "select ID, LNG, LAT as cords from MAP_POINT"
    cursor.execute(sql)
    results = cursor.fetchall()
    id_cords_map = {}
    for row in results:
        id_cords_map[row[0]] = [float(row[1]), float(row[2])]

    sql = "select m.ID, b.PATH, r.POINTS from MAP_POINT as m " \
          "join BOUNDARY as b on m.ID = b.ID " \
          "join REACHABLE_POINT as r on m.ID = r.ID;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        boundary_path_list = row[1].split(';')
        # 优化可达范围边界
        optimized_boundary_path_list = optimize_path(boundary_path_list)

        # 将 optimized_boundary_path_list 构造成poly
        poly = []
        for i in range(len(optimized_boundary_path_list) - 1):
            point1 = [float(optimized_boundary_path_list[i].split(',')[0]),
                      float(optimized_boundary_path_list[i].split(',')[1])]
            point2 = [float(optimized_boundary_path_list[i + 1].split(',')[0]),
                      float(optimized_boundary_path_list[i + 1].split(',')[1])]
            poly.append([point1, point2])
        # 过滤在边界内的点
        filtered_id_list = []
        if not row[2] == '':
            for id in row[2].split(';'):
                if is_poi_within_poly(id_cords_map[id], poly):
                    filtered_id_list.append(id)

        sql = "insert into BOUNDARY_OPTIMIZED (ID, PATH) values (%s, %s);"
        cursor.execute(sql, (row[0], ';'.join(optimized_boundary_path_list)))

        sql = "insert into REACHABLE_POINT_OPTIMIZED (ID, POINTS) values (%s, %s);"
        cursor.execute(sql, (row[0], ';'.join(filtered_id_list)))

        conn.commit()
       
        print("完成优化：" + row[0])

    cursor.close()
    conn.close()
