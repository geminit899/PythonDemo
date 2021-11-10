# -*- coding: utf-8 -*-
import sys
import copy
import conf
import time
import traceback
import alphashape
from logger import LOG
from utils import http_get, get_points_from_oracle, write_boundary_and_reachable_point_into_oracle, divide_list_to_parts


def get_surround_poi_list(location):
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
            results = http_get(conf.POI_URL, poi_param, 'POI')
            if len(results) == 0:
                break
            for result in results:
                poi_map[result['uid']] = str(result['location']['lat']) + ',' + str(result['location']['lng'])
            page_num += 1
    return poi_map.values()


def get_reachable_poi_list(location):
    """
    在已有点列表中，获取目标点周围15分钟内，可以步行达到的所有点
    :param:  location            如：39.915,116.404
    :return: reachable_poi_list  如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404']
    """
    # 根据目标点，获取以15分钟步程为半径，所有周围点，poi_list是一维数组
    poi_list = get_surround_poi_list(location)
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
        results = http_get(conf.RIDE_URL, ride_param, 'RIDE')
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
        results = http_get(conf.PATH_RIDE_URL, path_ride_param, 'PATH_RIDE')
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
        results = http_get(conf.BATCH_WALK_URL, batch_walk_param, 'BATCH_WALK')
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
    return []


def connect_boundary_point(boundary_point_list):
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
        results = http_get(conf.PATH_WALK_URL, path_walk_param, 'PATH_WALK')
        if 'routes' in results and len(results['routes']) > 0 and 'steps' in results['routes'][0]:
            steps = results['routes'][0]['steps']
            for j in range(len(steps)):
                step_path_list = steps[j]['path'].split(';')
                for k in range(len(step_path_list)):
                    if (j == 0 and k == 0) or k != 0:
                        two_point_path_list.append(step_path_list[k])
            boundary_path_list.append(two_point_path_list)
    return boundary_path_list


def get_boundary(reachable_poi_list):
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
    boundary_path_list = connect_boundary_point(boundary_point_list)
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


def filter_point(dataframe, points, type):
    """
    从dataframe中过滤出poi_list中有的数据
    :param dataframe: 现有资源点 pandas.dataframe中点row如：
    {
        'ID': '',
        'LNG': '',
        'LAT': '',
        'TYPE': ''
    }
    :param points  如：
    ['39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404', '39.915,116.404']
    :param type  当前目标点的类型，如果为house，则过滤资源点；如果不是house，则过滤小区点
    :return: reachable_resource_list ['ID', 'ID']
    """
    reachable_resource_list = []
    for row in dataframe.itertuples():
        if type == 'house' and row.TYPE == 'house':
            continue
        if type != 'house' and row.TYPE != 'house':
            continue
        point = str(row.LAT) + "," + str(row.LNG)
        if point in points:
            reachable_resource_list.append(row.ID)
    return reachable_resource_list


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

        # 处理出现错误的点ID
        error_row = []

        # 遍历所有小区，获取可达边界及可达资源点，并写入数据库
        for row in all_point.itertuples():
            if conf.START_FROM != '':
                if conf.START_FROM == row.ID:
                    conf.START_FROM = ''
                else:
                    continue
            time_start = time.time()
            message = 'ID:' + row.ID + ', 类型：' + row.TYPE
            try:
                # 目标点
                location = str(row.LAT) + "," + str(row.LNG)
                message += '，经纬度:' + location
                # 获取目标点周围步行15分钟可达点
                reachable_poi_list = get_reachable_poi_list(location)
                message += '，所有可达点个数:' + str(len(reachable_poi_list))
                # 根据所有可达点，获取可达范围边界
                boundary_path_list = get_boundary(reachable_poi_list)
                message += '，可达边界范围点个数:' + str(len(boundary_path_list))
                # 根据所有可达点，过滤出现有资源点
                reachable_filtered_list = filter_point(all_point, reachable_poi_list, row.TYPE)
                if row.TYPE == 'house':
                    message += '，可达资源点个数:'
                else:
                    message += '，可达小区点个数:'
                message += str(len(reachable_filtered_list))
                write_boundary_and_reachable_point_into_oracle(row.ID, boundary_path_list, reachable_filtered_list)
            except:
                error_row.append(row.ID)
                message += '，处理出现错误。'
                e = traceback.format_exc()
                if e is not None:
                    message += '错误详情：' + e
                LOG.error(message)
            else:
                time_end = time.time()
                message += '，一共花费 ' + str(round(time_end - time_start)) + '秒。'
                LOG.info(message)
            # 每个目标点使用一个AK，所有AK循环使用
            conf.AK_INDEX = (conf.AK_INDEX + 1) % len(conf.AK)

        if len(error_row) == 0:
            LOG.info('完成一次全体采集。所有点均处理成功。')
        else:
            LOG.error('完成一次全体采集。' + str(len(error_row)) + '个点处理出现错误：' + '; '.join(error_row))
