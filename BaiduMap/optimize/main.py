# -*- coding: utf-8 -*-
import sys
import copy
import conf
import math
import time
import threading
import traceback
import alphashape
from logger import LOG
from utils import http_get, get_points_from_oracle, write_boundary_and_reachable_point_into_oracle, \
    divide_list_to_parts, divide_df_to_parts


def get_surround_poi_list(location, ak):
    """
    获取目标点以15分钟步程为半径，范围内所有的点
    :param:  location 如：'39.915,116.404'
    :return: poi_list  如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404']
    """
    poi_map = {}
    poi_param = copy.deepcopy(conf.POI_PARAM)
    poi_param['location'] = location
    # 地点检索时必填的query，包含所有种类，获取所有点
    for tag in ["旅游景点", "美食", "酒店", "购物", "生活服务", "丽人", "旅游景点", "休闲娱乐", "运动健身", "教育培训", "文化传媒",
                "医疗", "汽车服务", "交通设施", "金融", "房地产", "公司企业", "政府机构"]:
        poi_param['query'] = tag
        page_num = 0
        while True:
            poi_param['page_num'] = page_num
            results = http_get(conf.POI_URL, poi_param, 'POI', ak)
            if len(results) == 0:
                break
            for result in results:
                poi_map[result['uid']] = str(result['location']['lat']) + ',' + str(result['location']['lng'])
            page_num += 1
    return poi_map.values()


def get_reachable_poi_list(location, ak):
    """
    在已有点列表中，获取目标点周围15分钟内，可以步行达到的所有点
    :param:  location            如：39.915,116.404
    :return: reachable_poi_list  如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404']
    """
    # 根据目标点，获取以15分钟步程为半径，所有周围点，poi_list是一维数组
    poi_list = get_surround_poi_list(location, ak)
    # 将所有周围点平均分成三份，分别使用三个接口
    poi_list_parts = divide_list_to_parts(poi_list, 3)
    ride_part = poi_list_parts[0]
    path_ride_part = poi_list_parts[1]
    batch_walk_part = poi_list_parts[2]

    # 声明变量用于存储所有最后的可达点
    reachable_poi_list = []
    # 使用骑行路径规划接口来判断可达点
    ride_param = copy.deepcopy(conf.RIDE_PARAM)
    ride_param['origin'] = location
    for poi in ride_part:
        if poi == location:
            continue
        ride_param['destination'] = poi
        results = http_get(conf.RIDE_URL, ride_param, 'RIDE', ak)
        if 'routes' in results and len(results['routes']) > 0 and 'distance' in results['routes'][0]:
            if results['routes'][0]['distance'] <= 1100:
                reachable_poi_list.append(poi)
    # 使用骑行路径规划接口来判断可达点
    path_ride_param = copy.deepcopy(conf.PATH_RIDE_PARAM)
    path_ride_param['origin'] = location
    for poi in path_ride_part:
        if poi == location:
            continue
        path_ride_param['destination'] = poi
        results = http_get(conf.PATH_RIDE_URL, path_ride_param, 'PATH_RIDE', ak)
        if 'routes' in results and len(results['routes']) > 0 and 'distance' in results['routes'][0]:
            if results['routes'][0]['distance'] <= 1100:
                reachable_poi_list.append(poi)
    # 使用批量算路接口来判断可达点
    batch_walk_param = copy.deepcopy(conf.BATCH_WALK_PARAM)
    batch_walk_param['origins'] = location
    for poi in batch_walk_part:
        if poi == location:
            continue
        batch_walk_param['destinations'] = poi
        results = http_get(conf.BATCH_WALK_URL, batch_walk_param, 'BATCH_WALK', ak)
        if len(results) > 0 and 'duration' in results[0] and 'value' in results[0]['duration']:
            if results[0]['duration']['value'] <= 900:
                reachable_poi_list.append(poi)
    return reachable_poi_list


def get_points_boundary(points):
    """
    使用AS算法获取边缘点顺序集合
    :param:  points     结构如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404'， '39.915,116.404']
    :return: 边界点顺序集合  结构如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404']
    """
    if len(points) == 0:
        return []
    alpha = 300
    while alpha >= 0:
        try:
            res = alphashape.alphashape(points, alpha)
            if res.type != 'Polygon':
                alpha = alpha - 1
                continue
            # 从边缘点中提取边缘tuple的顺序列表，列表项包含uid和location
            boundary_point_list = []
            x, y = res.boundary.coords.xy
            for i in range(len(x)):
                boundary_point_list.append(str(x[i]) + "," + str(y[i]))
            return boundary_point_list
        except:
            alpha = alpha - 1
            continue
    return []


def connect_boundary_point(boundary_point_list, ak):
    """
    遍历边缘点列表，按顺序依次获取两个边缘点之间的路径
    :param:  boundary_point_list  边界点顺序集合  结构如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404']
    :return: 边界点顺序集合  结构如：
    [
        ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404'],
        ['39.915,116.404', '39.915,116.404'],
        ['39.915,116.404', '39.915,116.404', '39.915,116.404'],
    ]
    """
    boundary_path_list = []
    for i in range(len(boundary_point_list) - 1):
        two_point_path_list = []
        path_walk_param = copy.deepcopy(conf.PATH_WALK_PARAM)
        path_walk_param['origin'] = boundary_point_list[i]
        path_walk_param['destination'] = boundary_point_list[i + 1]
        results = http_get(conf.PATH_WALK_URL, path_walk_param, 'PATH_WALK', ak)
        if 'routes' in results and len(results['routes']) > 0 and 'steps' in results['routes'][0]:
            steps = results['routes'][0]['steps']
            for j in range(len(steps)):
                step_path_list = steps[j]['path'].split(';')
                for k in range(len(step_path_list)):
                    if (j == 0 and k == 0) or k != 0:
                        two_point_path_list.append(step_path_list[k])
            boundary_path_list.append(two_point_path_list)
    return boundary_path_list


def get_boundary(reachable_poi_list, ak):
    """
    根据点列表，获取最外围的所有点，并将其按顺序一一连接，返回边界线上的所有点
    :param:  reachable_poi_list   可达点列表  如：
    ['39.915,116.404'， '39.915,116.404'， '39.915,116.404'， '39.915,116.404']
    :return: 边界点顺序集合  如：
    ['39.915,116.404'， '39.915,116.404'， '39.915,116.404'， '39.915,116.404']
    """
    # 从reachable_poi中获取所有点的tuple(x, y)
    points = []
    for poi in reachable_poi_list:
        location_arr = poi.split(',')
        points.append((float(location_arr[0]), float(location_arr[1])))
    # 使用AS算法获取边缘点的顺序列表，boundary_point_list是一维数组
    boundary_point_list = get_points_boundary(points)
    # 遍历边缘点列表，按顺序依次获取两个边缘点之间的路径，boundary_path_list是二维数组
    boundary_path_list = connect_boundary_point(boundary_point_list, ak)
    # 清除相邻两个边缘点路径的重合部分
    for i in range(len(boundary_path_list)):
        suf_index = (i + 1) % len(boundary_path_list)
        for p in boundary_path_list[i]:
            if p in boundary_path_list[suf_index]:
                boundary_path_list[i] = boundary_path_list[i][:boundary_path_list[i].index(p) + 1]
                boundary_path_list[suf_index] = boundary_path_list[suf_index][
                                                boundary_path_list[suf_index].index(p) + 1:]
                break
    # 按顺序把所有边缘路径连接成一条路径，boundary_path_point_list是一维数组
    boundary_path_point_list = []
    for boundary_path in boundary_path_list:
        boundary_path_point_list.extend(boundary_path)
    if len(boundary_path_point_list) > 0:
        boundary_path_point_list.append(boundary_path_point_list[0])
    return boundary_path_point_list


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


def filter_point(dataframe, points, optimized_boundary_path_list, type):
    """
    从dataframe中过滤出poi_list中有的数据，并保证每个点都在可达区域内
    :param dataframe: 现有资源点 pandas.dataframe中点row如：
    {
        'ID': '',
        'LNG': '',
        'LAT': '',
        'TYPE': ''
    }
    :param points  如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404']
    :param optimized_boundary_path_list 优化后的可达边界点列表，如：
    ['39.915,116.404'， '39.915,116.404'， '39.915,116.404']
    :param type  当前目标点的类型，如果为house，则过滤资源点；如果不是house，则过滤小区点
    :return: reachable_resource_list ['ID', 'ID']
    """
    # 将 optimized_boundary_path_list 构造成poly
    poly = []
    for i in range(len(optimized_boundary_path_list) - 1):
        point1 = [float(optimized_boundary_path_list[i].split(',')[0]),
                  float(optimized_boundary_path_list[i].split(',')[1])]
        point2 = [float(optimized_boundary_path_list[i + 1].split(',')[0]),
                  float(optimized_boundary_path_list[i + 1].split(',')[1])]
        poly.append([point1, point2])

    # 根据type，从dataframe中过滤出poi_list中有的数据
    reachable_resource_list = []
    for row in dataframe.itertuples():
        if type == 'house' and row.TYPE == 'house':
            continue
        if type != 'house' and row.TYPE != 'house':
            continue
        point = str(row.LAT) + "," + str(row.LNG)
        if point in points and is_poi_within_poly([float(row.LAT), float(row.LNG)], poly):
            # 依次判断是否在poly内部
            reachable_resource_list.append(row.ID)

    return reachable_resource_list


def process_thread(all_point, part_point, ak_list, error_row):
    # 遍历所有小区，获取可达边界及可达资源点，并写入数据库
    ak_index = 0
    for row in part_point.itertuples():
        ak = ak_list[ak_index]
        time_start = time.time()
        message = 'ID:' + row.ID + ', AK:' + ak
        try:
            # 目标点
            location = str(row.LAT) + "," + str(row.LNG)
            message += '，经纬度:' + location
            # 获取目标点周围步行15分钟可达点
            reachable_poi_list = get_reachable_poi_list(location, ak)
            message += '，可达点个数:' + str(len(reachable_poi_list))
            # 根据所有可达点，获取可达范围边界
            boundary_path_list = get_boundary(reachable_poi_list, ak)
            message += '，可达边界点个数:' + str(len(boundary_path_list))
            # 优化可达范围边界
            optimized_boundary_path_list = optimize_path(boundary_path_list)
            # 根据所有可达点，以及是否在优化后的可达范围边界内，过滤出现有资源点
            reachable_filtered_list = filter_point(all_point, reachable_poi_list, optimized_boundary_path_list, row.TYPE)
            if row.TYPE == 'house':
                message += '，可达资源点个数:'
            else:
                message += '，可达小区点个数:'
            message += str(len(reachable_filtered_list))
            write_boundary_and_reachable_point_into_oracle(row.ID, optimized_boundary_path_list, reachable_filtered_list)
        except:
            error_row.append(row.ID)
            message += '，处理出现错误。'
            e = traceback.format_exc()
            if e is not None:
                message += '错误详情：' + e
            LOG.error(message)
        else:
            time_end = time.time()
            message += '，花费' + str(round(time_end - time_start)) + '秒。'
            LOG.info(message)
        # 每个目标点使用一个AK，所有AK循环使用
        ak_index = (ak_index + 1) % len(ak_list)


if __name__ == '__main__':
    # 循环处理全体数据
    while True:
        # 从数据库中读取所有小区及资源点，all_point结构：pandas.dataframe
        try:
            all_point = get_points_from_oracle()
        except:
            error_message = '从数据库获取所有点时发生错误。'
            e = traceback.format_exc()
            if e is not None:
                error_message += '错误详情：' + e
            LOG.error(error_message)
            sys.exit(1)
        else:
            LOG.info('已从数据库获取所有点，长度为：' + str(all_point.__len__()))

        all_point_parts = divide_df_to_parts(all_point, conf.THREAD_NUM)
        aks = divide_list_to_parts(conf.AK, conf.THREAD_NUM)

        # 处理出现错误的点ID
        error_row = []

        thread_list = []
        for i in range(len(all_point_parts)):
            thread_list.append(threading.Thread(target=process_thread, args=(all_point, all_point_parts[i], aks[i], error_row)))
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()

        if len(error_row) == 0:
            LOG.info('完成一次全体采集。所有点均处理成功。')
        else:
            LOG.error('完成一次全体采集。' + str(len(error_row)) + '个点处理出现错误：' + '; '.join(error_row))
