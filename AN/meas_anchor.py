import numpy as np


'''
0) 天然就有的，anchor的特征位置，load之后就已经有了，到时直接取用即可
1) 从meas中去找特征位置 getDoubleRegionStartPoints
2) anchor的特征位置 & 1中的meas的特征位置，求整个站区间的映射关系getMappingInfo，可以得到一个各个子区间映射参数集
3) 遍历此站区间内所有点，看该点在哪个子区间，求映射后的里程位置
    - 非双线区域可以采样
    - 双线是不可以采样的
'''
def getDoubleRegionStartPoints(list_distance, list_stagger_other,stations):
    DoubleRegionDict={}
    if len(list_distance) != len(list_stagger_other):
        return list()
    # list_double_region_start_distance = list()
    # point_station = list()
    for i in range(len(list_distance)):
        if list_stagger_other[i] is None:
            continue

        # check if previous is not
        if i > 0 and list_stagger_other[i-1] is not None:
            continue

        if stations[i] not in DoubleRegionDict.keys():
            DoubleRegionDict[stations[i]]=[]
        if len(DoubleRegionDict[stations[i]]) > 1 and (list_distance[i] - DoubleRegionDict[stations[i]][-1] < 50):
            continue
        DoubleRegionDict[stations[i]].append(list_distance[i])
        # list_double_region_start_distance.append(list_distance[i])
        # point_station.append(stations[i])
    print(DoubleRegionDict)
    return DoubleRegionDict
    # return list_double_region_start_distance,point_station


'''
# map data from [meas_s, meas_e] ---> [anchor_s, anchor_e]
usage:
    meas * ratio + offset ===> anchor
'''
class MappingInfo(object):
    def __init__(self) -> None:
        self.offset_meas_to_anchor = 0
        self.ratio_meas_to_anchor = 1.0
        self.dist_meas_s = 0
        self.dist_meas_e = 0
    
    def proc(self, dist_meas):
        return dist_meas*self.ratio_meas_to_anchor + self.offset_meas_to_anchor


# def getMappingInfo(list_double_region_distance_meas, list_double_region_distance_anchor):
#     list_mapping_info = list()
#     num_key_pt_meas = len(list_double_region_distance_meas)

#     num_key_pt_anchor = len(list_double_region_distance_anchor)
#     list_double_region_distance_meas=np.asarray(list_double_region_distance_meas)
#     list_double_region_distance_anchor=np.asarray(list_double_region_distance_anchor)
#     if num_key_pt_meas == 0 or num_key_pt_anchor == 0:
#         return list_mapping_info

#     for i in range(num_key_pt_meas):
#         print('i',i)
#         if i >= num_key_pt_anchor:
#             return list_mapping_info

#         dist_meas_s = 0
#         dist_anchor_s = 0
#         if i > 0:
#             dist_meas_s = list_double_region_distance_meas[i-1]
#             dist_anchor_s = list_double_region_distance_anchor[i-1]
#         dist_meas_e = list_double_region_distance_meas[i]
#         dist_anchor_e = list_double_region_distance_anchor[i]
#         dist_len_meas = dist_meas_e - dist_meas_s
#         dist_len_anchor = dist_anchor_e - dist_anchor_s

#         mapping_info = MappingInfo()
#         mapping_info.dist_meas_s = dist_meas_s
#         mapping_info.dist_meas_e = dist_meas_e
#         mapping_info.ratio_meas_to_anchor = dist_len_anchor / dist_len_meas
#         mapping_info.offset_meas_to_anchor = dist_anchor_s - dist_meas_s
#         list_mapping_info.append(mapping_info)
#     #     print('**************')
#     #     print(i)
#     #     print(dist_meas_s)
#     #     print(dist_meas_e)
#     #     print(mapping_info.ratio_meas_to_anchor)
#     #     print(mapping_info.offset_meas_to_anchor)
#     # print('lens',len(list_mapping_info))
#     return list_mapping_info


def getMappingInfo(list_double_region_distance_meas, list_double_region_distance_anchor):
    list_mapping_info = list()
    num_key_pt_meas = len(list_double_region_distance_meas)
    num_key_pt_anchor = len(list_double_region_distance_anchor)
    if num_key_pt_meas == 0 or num_key_pt_anchor == 0:
        return list_mapping_info
    list_double_region_distance_meas=np.asarray(list_double_region_distance_meas)
    list_double_region_distance_anchor=np.asarray(list_double_region_distance_anchor)
    for i in range(num_key_pt_meas):
        if i >= num_key_pt_anchor:
            return list_mapping_info

        dist_meas_s = 0
        dist_anchor_s = 0
        if i > 0:
            dist_meas_s = list_double_region_distance_meas[i-1]
            dist_anchor_s = list_double_region_distance_anchor[i-1]
        dist_meas_e = list_double_region_distance_meas[i]
        dist_anchor_e = list_double_region_distance_anchor[i]
        dist_len_meas = dist_meas_e - dist_meas_s
        dist_len_anchor = dist_anchor_e - dist_anchor_s

        mapping_info = MappingInfo()
        mapping_info.dist_meas_s = dist_anchor_s
        mapping_info.dist_meas_e = dist_len_meas
        mapping_info.ratio_meas_to_anchor = dist_len_anchor / dist_len_meas
        mapping_info.offset_meas_to_anchor = dist_anchor_s - dist_meas_s
        list_mapping_info.append(mapping_info)

    return list_mapping_info