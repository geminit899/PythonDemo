# -*- coding: utf-8 -*-
# oracle数据库配置
ORACLE_URL = '192.168.0.114:1521/helowin'
ORACLE_NAME = 'BDMAPS'
ORACLE_PASSWORD = 'BDMAPS'

# 开几个线程
THREAD_NUM = 2

# 百度地图AK配置，每个AK都有3万条配额/天/接口
AK = ['umCXbE27GqcbCuqlFOga5UQc4TNNYlxk', 'kBNzo7ovDo7Sh4yh2PtNyuo0FiapPbgj', 'gu7fLpPo9x9LfqGbVcH467YuA2QwVbf5',
      '4CqkTApXPUW6jAjEE82G2uG68iucaqut', 'y782G5eLTMMgM4iU4ScAMld2zXe6mXL6', 'ZiZ8Rwy1wGRAxGGc5snBKnLKMD8Nyhv8',
      '6aH4Ny4GKrrS6L2VjsxknTIw46LzqaYT', 'ShVxT2hfkdp5dFKFOSRdBYvAukLIflYf', 'Ovxj0WwIHne4gsVGoRO7rn6dIyhIeYaW',
      'aW80l5yuHWOgkcyBL2OpUxw00xvbsHBa']

# http请求返回值的key，按类型分
HTTP_RESPONSE_KEY = {
    'POI': 'results',
    'RIDE': 'result',
    'PATH_WALK': 'result',
    'PATH_RIDE': 'result',
    'BATCH_WALK': 'result'
}

# 地点检索接口，用于检索目标点周围所有点
POI_URL = 'https://api.map.baidu.com/place/v2/search'
POI_PARAM = {
    "query": "",
    "location": "",
    "radius": "1100",  # 以15分钟步程为半径
    "output": "json",
    "ak": '',
    "page_size": 20,
    "page_num": 0
}

# 骑行路径规划接口，用于获取两点之间的距离
RIDE_URL = 'https://api.map.baidu.com/direction/v2/riding'
RIDE_PARAM = {
    "origin": "",
    "destination": "",
    "output": "json",
    "ak": ''
}

# 步行路径规划（轻量）接口，用于获取区域边界
PATH_WALK_URL = 'https://api.map.baidu.com/directionlite/v1/walking'
PATH_WALK_PARAM = {
    "origin": "",
    "destination": "",
    "output": "json",
    "ak": ''
}

# 骑行路径规划（轻量）接口，用于获取两点之间的距离
PATH_RIDE_URL = 'https://api.map.baidu.com/directionlite/v1/riding'
PATH_RIDE_PARAM = {
    "origin": "",
    "destination": "",
    "output": "json",
    "ak": ''
}

# 批量算路接口，用于获取两点之间的距离
BATCH_WALK_URL = 'https://api.map.baidu.com/routematrix/v2/walking'
BATCH_WALK_PARAM = {
    "origins": "",
    "destinations": "",
    "output": "json",
    "ak": ''
}
