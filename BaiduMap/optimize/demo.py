import math
import pymysql


# -*- coding: utf-8 -*-
def clear_extra_duplicate_points(arr):
    length = 0
    if arr:
        p = 10001
        m = len(arr)
        for i in range(m):
            if p != arr[i]:
                p = arr[i]
                arr[length] = p
                length += 1
    result = []
    for i in range(0, length):
        result.append(arr[i])
    return result


# def clear_duplicate_path(points):
#     """
#     去除重复路段
#     :param:  points     结构如：
#     ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404'， '39.915,116.404']
#     :return: 边界点顺序集合  结构如：
#     ['39.915,116.404', '39.915,116.404', '39.915,116.404']
#     """
#     # 去除相邻的重复点
#     points = clear_extra_duplicate_points(points)
#     # 找到对称中心点
#     symmetrical_point_indexes = []
#     for i in range(1, len(points) - 1):
#         if points[i - 1] == points[i + 1]:
#             symmetrical_point_indexes.append(i)
#     # traverse symmetrical_point_indexes clear symmetrical points
#     clear_indexes = []
#     for symmetrical_point_index in symmetrical_point_indexes:
#         left_index = symmetrical_point_index - 1
#         right_index = symmetrical_point_index + 1
#         while True:
#             if points[left_index] == points[right_index]:
#                 left_index = left_index - 1 if left_index - 1 > 0 else len(points) - 1
#                 right_index = right_index + 1 if right_index + 1 < len(points) else 0
#             else:
#                 if left_index > right_index:
#                     for i in range(0, right_index):
#                         clear_indexes.append(i)
#                     for i in range(left_index, len(points)):
#                         clear_indexes.append(i)
#                 else:
#                     for i in range(left_index, right_index):
#                         clear_indexes.append(i)
#                 break
#     clear_indexes.sort(reverse=True)
#     for index in clear_indexes:
#         del points[index]
#     return points


def clear_duplicate_path(point_list):
    """
    去除重复路段
    :param:  points     结构如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404'， '39.915,116.404']
    :return: 边界点顺序集合  结构如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404']
    """
    # while True:
    #     cleared = False
    #     # 去除相邻的重复点
    #     point_list = clear_extra_duplicate_points(point_list)
    #     # 去除同一直线上多余点
    #     for i in reversed(range(0, len(point_list) - 1)):
    #         # 获取相邻三个点坐标，判断是否在一条直线上
    #         point1 = point_list[i + 1]
    #         point2 = point_list[i]
    #         point3 = point_list[i - 1]
    #         point1_x = float(point1.split(',')[0])
    #         point1_y = float(point1.split(',')[1])
    #         point2_x = float(point2.split(',')[0])
    #         point2_y = float(point2.split(',')[1])
    #         point3_x = float(point3.split(',')[0])
    #         point3_y = float(point3.split(',')[1])
    #         # 若纵坐标相等，则在一条直线上
    #         if point2_x - point1_x == 0 or point3_x - point2_x == 0:
    #             if point1_x == point2_x == point3_x:
    #                 cleared = True
    #                 del point_list[i]
    #             continue
    #         k12 = (point2_y - point1_y) / (point2_x - point1_x)
    #         k23 = (point3_y - point2_y) / (point3_x - point2_x)
    #         if k12 == k23:
    #             cleared = True
    #             del point_list[i]
    #     #
    #     if not cleared:
    #         break

    #
    point_map = {}
    point_map_duplicate_keys = set()
    for i in range(0, len(point_list)):
        if point_list[i] in point_map:
            point_map_duplicate_keys.add(point_list[i])
            point_map[point_list[i]].append(i)
        else:
            point_map[point_list[i]] = [i]
    to_be_deleted_indexes = set()
    for key in point_map_duplicate_keys:
        point_map_duplicate_indexes = point_map[key]
        point_map_duplicate_indexes.sort()
        # 不同index之间的距离
        indexes_lengths = []
        for i in range(0, len(point_map_duplicate_indexes)):
            if i + 1 < len(point_map_duplicate_indexes):
                indexes_lengths.append(point_map_duplicate_indexes[i + 1] - point_map_duplicate_indexes[i])
            else:
                indexes_lengths.append(point_map_duplicate_indexes[0] +
                                       len(point_list) - point_map_duplicate_indexes[i])
        # 不同点作为left_index时的总长度
        index_total_lengths = []
        for i in range(0, len(indexes_lengths)):
            total_length = 0
            for j in range(0, len(indexes_lengths) - 1):
                k = i + j
                if k >= len(indexes_lengths):
                    k = k % len(indexes_lengths)
                total_length += indexes_lengths[k]
            index_total_lengths.append(total_length)
        left_index = point_map_duplicate_indexes[index_total_lengths.index(min(index_total_lengths))]
        right_index = point_map_duplicate_indexes[index_total_lengths.index(min(index_total_lengths)) - 1]
        if left_index < right_index:
            for i in range(left_index, right_index):
                to_be_deleted_indexes.add(i)
        else:
            for i in range(0, right_index):
                to_be_deleted_indexes.add(i)
            for i in range(left_index, len(point_list)):
                to_be_deleted_indexes.add(i)
    to_be_deleted_indexes_list = list(to_be_deleted_indexes)
    to_be_deleted_indexes_list.sort()
    to_be_deleted_indexes_list.reverse()
    for index in to_be_deleted_indexes_list:
        del point_list[index]


    #
    # max_duplicate_length = 100
    # if len(point_list) > max_duplicate_length:
    #     i = len(point_list) - 1
    #     while i > max_duplicate_length:
    #         duplicate_point_index = -1
    #         for j in range(1, max_duplicate_length + 1):
    #             if point_list[i] == point_list[i - j]:
    #                 duplicate_point_index = i - j
    #         if not duplicate_point_index == -1:
    #             for k in range(duplicate_point_index, i):
    #                 del point_list[k]
    #             i = duplicate_point_index
    #         else:
    #             i -= 1
    if len(point_list) > 0 and not point_list[0] == point_list[len(point_list) - 1]:
        point_list.append(point_list[0])
    return point_list


def clear_narrow_path(points):
    if len(points) < 4:
        return points

    point_point_length_map = {}
    for i in range(0, len(points) - 1):
        point1 = points[i]
        for j in range(i + 1, len(points)):
            point2 = points[j]
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

    to_be_deleted_indexes = set()
    for point in point_point_length_map:
        to_point_length = point_point_length_map[point]
        sorted_point_length_list = sorted(to_point_length.items(), key=lambda x:x[1], reverse=False)
        first_near_point = sorted_point_length_list[0][0]
        first_near_length = sorted_point_length_list[0][1]
        second_near_point = sorted_point_length_list[1][0]
        second_near_length = sorted_point_length_list[1][1]
        point_index = points.index(point)

        if first_near_length > 0.0009 or second_near_length > 0.0009:
            continue

        nearest_two_point_index = []
        if points[point_index - 1] == first_near_point and points[point_index + 1] == second_near_point:
            continue
        elif points[point_index - 1] == second_near_point and points[point_index + 1] == first_near_point:
            continue
        elif points[point_index - 1] == first_near_point or points[point_index - 1] == second_near_point:
            nearest_two_point_index.append(points.index(first_near_point))
            nearest_two_point_index.append(points.index(second_near_point))
        elif points[point_index + 1] == second_near_point or points[point_index + 1] == second_near_point:
            nearest_two_point_index.append(points.index(first_near_point))
            nearest_two_point_index.append(points.index(second_near_point))
        else:
            nearest_two_point_index.append(points.index(first_near_point))
            nearest_two_point_index.append(points.index(second_near_point))

        tow_indexes_between = math.fabs(nearest_two_point_index[0] - nearest_two_point_index[1])
        if len(points) / 2 > tow_indexes_between:
            for i in range(min(nearest_two_point_index) + 1, max(nearest_two_point_index)):
                to_be_deleted_indexes.add(i)
        else:
            for i in range(0, min(nearest_two_point_index)):
                to_be_deleted_indexes.add(i)
            for i in range(max(nearest_two_point_index) + 1, len(points)):
                to_be_deleted_indexes.add(i)

    to_be_deleted_indexes_list = list(to_be_deleted_indexes)
    to_be_deleted_indexes_list.sort()
    to_be_deleted_indexes_list.reverse()
    for index in to_be_deleted_indexes_list:
        del points[index]

    # 将 boundary_path_list 首尾相连
    if len(points) > 0 and not points[0] == points[len(points) - 1]:
        points.append(points[0])

    return points


if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', user='root', passwd='hack', db='bdmap', charset='utf8mb4')
    cursor = conn.cursor()
    sql = "select concat_ws(',', m.LAT, m.LNG) as cords, b.PATH from MAP_POINT as m join BOUNDARY_OPTIMIZED as b on m.ID = b.ID;"
    sql = "select concat_ws(',', m.LAT, m.LNG) as cords, b.PATH from BOUNDARY_OPTIMIZED as b join MAP_POINT as m on m.ID = b.ID;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        cords = row[0]
        path = row[1]
        points = path.split(';')

        # points = clear_duplicate_path(points)
        # points = clear_narrow_path(points)

        file = open("/Users/geminit/Desktop/conf.txt")
        html = file.read()
        html = html.replace("var center = '';", "var center = '" + cords + "';")
        html = html.replace("var pathListSTR = '';", "var pathListSTR = '" + path + "';")
        html = html.replace("var pathList = [];", "var pathList = " + str(points) + ";")

        file = open("/Users/geminit/WebstormProjects/BaiduGIS/online/demo.html", "w")
        file.write(html)
        file.close()

        print(1)



    # point_str = ''
    # points = point_str.split(';')
    # print(len(points))
    # points = clear_duplicate_path(points)
    # print(len(points))
    # print(points)
