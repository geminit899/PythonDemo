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
    sinsc=0
    # 循环每条边的曲线->each polygon 是二维数组[[x1,y1],…[xn,yn]]
    for epoly in poly:
        for i in range(len(epoly)-1):
            s_poi = epoly[i]
            e_poi = epoly[i+1]
            if is_ray_intersects_segment(poi, s_poi, e_poi):
                # 有交点就加1
                sinsc += 1
    return True if sinsc % 2 == 1 else False

if __name__ == '__main__':
    poi = [1, 8]
    path = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9],
            [1, 9], [2, 9], [3, 9], [4, 9], [5, 9],
            [5, 8], [4, 8], [3, 8], [2, 8],
            [2, 7], [2, 6], [2, 5], [2, 4],
            [3, 4], [4, 4], [5, 4], [6, 4], [7, 4],
            [7, 5], [7, 6], [7, 7], [7, 8],
            [6, 8],
            [6, 9], [7, 9], [8, 9], [9, 9],
            [9, 8], [9, 7], [9, 6], [9, 5], [9, 4], [9, 3], [9, 2], [9, 1], [9, 0],
            [8, 0], [7, 0], [6, 0], [5, 0], [4, 0], [3, 0], [2, 0], [1, 0], [0, 0]]
    poly = []
    for i in range(len(path) - 1):
        poly.append([path[i], path[i + 1]])
    res = is_poi_within_poly(poi, poly)
    print(res)
