import numpy as np
from AN.mapping import *
# import matplotlib.pyplot as plt


def getKeyPoints(list_distance, list_stagger_other, th_min_span = 12):
    if len(list_distance) != len(list_stagger_other):
        return list()
    list_kp = list()
    for i in range(len(list_distance)):
        if list_stagger_other[i] is None:
            continue
        # check if previous is not
        if i > 0 and list_stagger_other[i-1] is not None:
            continue
        # check if last too near
        if len(list_kp) > 1 and (list_distance[i] - list_kp[-1] < th_min_span):
            continue
        list_kp.append(list_distance[i])
    return list_kp


def getKeyPointsPlus(list_distance, list_stagger, list_stagger_other, th_min_span = 12):
    # print('list_stagger))))))))))))))))\n',list_stagger)
    if len(list_distance) != len(list_stagger_other):
        return list()
    if len(list_stagger) != len(list_stagger_other):
        return list()
    list_kp = list()

    for i in range(len(list_distance)):
        flag_kp_found = False
        dist_this = list_distance[i]
        while True:
            if list_stagger_other[i] is None:
                break
            # check if previous is not
            if i > 0 and list_stagger_other[i-1] is not None:
                break
            # check if last too near
            if len(list_kp) > 0 and (dist_this - list_kp[-1] < th_min_span):
                break
            list_kp.append(dist_this)
            flag_kp_found = True
            break

        if flag_kp_found:
            continue

        if i == 0:
            continue

        stagger_pre = list_stagger[i-1]
        stagger = list_stagger[i]
        # print('list_stagger^^^^^^^^^^^^^^^\n',list_stagger)
        if (stagger > 0 and stagger_pre > 0) or (stagger < 0 and stagger_pre < 0):
            continue
        if abs(stagger - stagger_pre) < 200:
            continue
        if abs(stagger - stagger_pre) > 330:
            continue
        
        # check if last too near
        if len(list_kp) > 0 and (list_distance[i] - list_kp[-1] < th_min_span):
            continue
        list_kp.append(list_distance[i])
    # print('list_kp')
    # print(list_kp)
    return list_kp


'''
独立工具函数2
根据拉出值(stagger与stagger_other)获得双线特征的位置Plus版本
除判断依据是基于拉出值2是否为None之外，还根据拉出值的数值变化判断是否存在双线特征位置
返回值
    list_kp, 双线位置（即keypoint）处的里程
    list_index_missing, 拉出值2不为None但是据数值变化认为存在双线结构的index位置，此index信息可用于后续补点
'''
def getKeyPointsPlus2(list_distance, list_stagger, list_stagger_other, th_min_span = 12):
    if len(list_distance) != len(list_stagger_other):
        return list(), list()
    if len(list_stagger) != len(list_stagger_other):
        return list(), list()
    list_kp = list()
    list_index_missing = list()

    for i in range(len(list_distance)):
        flag_kp_found = False
        dist_this = list_distance[i]
        while True:
            if list_stagger_other[i] is None:
                break
            # check if previous is not
            if i > 0 and list_stagger_other[i-1] is not None:
                break
            # check if last too near
            if len(list_kp) > 0 and (dist_this - list_kp[-1] < th_min_span):
                break
            list_kp.append(dist_this)
            flag_kp_found = True
            # print('\n\n\n')
            # print(list_distance[i-50:i+50])
            # print(list_stagger[i-50:i+50])
            # print(list_stagger_other[i-50:i+50])
            break

        if flag_kp_found:
            continue

        if i == 0:
            continue

        # check if keypoint missing
        stagger_pre = list_stagger[i-1]
        stagger = list_stagger[i]
        if (stagger > 0 and stagger_pre > 0) or (stagger < 0 and stagger_pre < 0):
            continue
        if abs(stagger - stagger_pre) < 280:
            continue
        if abs(stagger - stagger_pre) > 340:
            continue
        
        # check if last too near
        if len(list_kp) > 0 and (list_distance[i] - list_kp[-1] < th_min_span):
            continue
        list_kp.append(list_distance[i])
        list_index_missing.append(i)
    return list_kp, list_index_missing
# 工具函数，由x1, x2得到x3, 假定2*x2 = x1 + x3
def extraplot(x1, x2, max_diff = 10):
    diff = abs(x2 - x1)
    if diff > max_diff:
        diff = max_diff
    diff = diff if x2 > x1 else -diff
    return x2 + diff
# 工具函数，一对数值的排序
def getOrderedStaggerPair(s1, s2):
    if s1 < s2:
        return s1, s2
    return s2, s1

'''
独立工具函数3
根据之前的 getKeyPointsPlus 函数，可获得补点的位置
本函数可在补点位置处，对拉出值(stagger与stagger_other)插入额外的点，使之在双线结构处构成一小段平行的双线结构
另外，对于其他测量向量，可作为附加入参传入，函数对其进行补点
输入与getKeyPointsPlus完全一致，将修改拉出值(stagger与stagger_other)的值
注意，补点不会增加向量的元素个数只是修改拉出值(stagger与stagger_other)的值
'''
def addMissingMeas(list_distance, list_stagger, list_stagger_other, th_min_span = 12):
   
    list_kp, list_index_missing = getKeyPointsPlus2(list_distance, list_stagger, list_stagger_other, th_min_span)
    print("********addMissingMeas********\t",len(list_kp),len(list_index_missing))
    if len(list_kp) == 0 or len(list_index_missing) == 0:
        print('no keypoint found')
        return False
    
    for index in list_index_missing:
        # 补点位置前后几个点均在list范围内，无需判断index是否越界
        stagger_dummy_other = extraplot(list_stagger[index+1], list_stagger[index])
        stagger_dummy_main  = extraplot(list_stagger[index-2], list_stagger[index-1])

        # 处理index-2
        # list_stagger[index-2], list_stagger_other[index-2] = getOrderedStaggerPair(stagger_dummy_other, list_stagger[index-2])

        # 处理index-1
        list_stagger[index-1], list_stagger_other[index-1] = getOrderedStaggerPair(stagger_dummy_other, list_stagger[index-1])

        # 处理index
        list_stagger[index], list_stagger_other[index] = getOrderedStaggerPair(stagger_dummy_main, list_stagger[index])

        # 处理index+1
        list_stagger[index+1], list_stagger_other[index+1] = getOrderedStaggerPair(stagger_dummy_main, list_stagger[index+1])

        # 处理index+2
        list_stagger[index+2], list_stagger_other[index+2] = getOrderedStaggerPair(stagger_dummy_main, list_stagger[index+2])
    return True



class MeasInOneStation(object):
    def __init__(self, id_station_next) -> None:
        self.id_station_next = id_station_next
        self.list_dist = list()
        self.list_stagger = list()
        self.list_stagger_other = list()
        self.list_height = list()
        self.list_kp = list()

    def add(self, dist, stagger, stagger_other, height):
        self.list_dist.append(dist)
        self.list_stagger.append(stagger)
        self.list_stagger_other.append(stagger_other)
        self.list_height.append(height)

    def getGeoData(self):
        self.list_kp = getKeyPoints(self.list_dist, self.list_stagger_other)
        self.list_kp_plus = getKeyPointsPlus(self.list_dist, self.list_stagger, self.list_stagger_other)
        return self.list_dist, self.list_stagger, self.list_stagger_other, self.list_kp, self.list_kp_plus
        
class Meas(object):
    def __init__(self, flag_ul_or_dl) -> None:
        self.flag_ul_or_dl = flag_ul_or_dl
        self.dict_stations = dict()

    def __parseFloat(self, string):
        return float(string) if 'None' not in string else None

    def load(self, file_meas):
        #                           4   5           6                               11   12     13      14                            
        #时间,时间,终点站,上一站,下一站,车速,距上一站驶出距离,方向,趟次,anchor,flag,导高,拉出值,导高(2),拉出值(2),磨耗,最低温度,平均温度,最高温度
        self.dict_stations = dict()
        with open(file_meas, 'r', encoding='utf-8') as f:
            f.readline()# skip the first line
            for line in f:
                list_str = line.split(',')
                if len(list_str) != 19:
                    continue
                id_station_next = int(list_str[4])
                dist = float(list_str[6])
                height = self.__parseFloat(list_str[11])
                stagger = self.__parseFloat(list_str[12])
                stagger_other = self.__parseFloat(list_str[14])
                if id_station_next not in self.dict_stations:
                    self.dict_stations[id_station_next] = MeasInOneStation(id_station_next)
                self.dict_stations[id_station_next].add(dist, stagger, stagger_other, height)

    def getGeoData(self, list_id_station_next_selected = list()):
        list_dist_all = list()
        list_stagger_all = list()
        list_stagger_other_all = list()
        list_dist_kp_all = list()
        list_dist_kp_plus_all = list()
        list_dist_station_start_all = list()
        list_id_station_next_all = list()
        
        list_station = list(self.dict_stations.keys())
        dist_preall = 0
        for i in range(len(list_station)):
            key = list_station[i]

            if len(list_id_station_next_selected) != 0:
                if key not in list_id_station_next_selected:
                    continue
            
            list_id_station_next_all.append(key)
            list_dist, list_stagger, list_stagger_other, list_dist_kp, list_dist_kp_plus = self.dict_stations[key].getGeoData()
            list_dist_all += list(np.asarray(list_dist) + dist_preall)
            list_dist_kp_all += list(np.asarray(list_dist_kp) + dist_preall)
            list_dist_kp_plus_all += list(np.asarray(list_dist_kp_plus) + dist_preall)
            list_stagger_all += list_stagger
            list_stagger_other_all += list_stagger_other
            list_dist_station_start_all.append(dist_preall)
            dist_preall = list_dist_all[-1]
        return list_dist_all, list_stagger_all, list_stagger_other_all, list_dist_kp_all, list_dist_kp_plus_all, list_dist_station_start_all, list_id_station_next_all

    def getListNextStation(self):
        list_id_next_station = list(self.dict_stations.keys())
        return list_id_next_station

    # def plot(self, list_id_station_next_selected = list()):
    #     list_dist, list_stagger, list_stagger_other, list_dist_kp, list_dist_kp_plus, list_dist_station_start, list_id_station_next = self.getGeoData(list_id_station_next_selected)
    #     # plt.figure()
    #     # plt.subplot(2, 1, 1)
    #     figure, (ax1) = plt.subplots(1, 1, sharex=True)
    #     ax1.plot(list_dist, list_stagger)
    #     for dist in list_dist_kp:
    #         ax1.plot([dist, dist], [-300, 300], 'r')
    #     for dist in list_dist_kp_plus:
    #         ax1.plot([dist, dist], [-300, 300], 'r', linestyle='dashed')
    #     for i in range(len(list_dist_station_start)):
    #         dist = list_dist_station_start[i]
    #         id_station_next = list_id_station_next[i]
    #         ax1.plot([dist, dist], [-400, 400], 'g', linestyle='dashed')
    #         ax1.annotate(text=f'#{id_station_next}',  xytext=(dist+10, 500), xy=(dist, 350), arrowprops=dict(arrowstyle="<-"))
    #     plt.show()

'''
0) 天然就有的，anchor的特征位置，load之后就已经有了，到时直接取用即可
1) 从meas中去找特征位置 getKeyPoints
2) anchor的特征位置 & 1中的meas的特征位置，求整个站区间的映射关系getMappingInfo，可以得到一个各个子区间映射参数集
3) 遍历此站区间内所有点，看该点在哪个子区间，求映射后的里程位置
    - 非双线区域可以采样
    - 双线是不可以采样的
'''


def getMappingInfo(list_double_region_distance_meas, list_double_region_distance_anchor):
    list_mapping_info = list()
    num_key_pt_meas = len(list_double_region_distance_meas)
    num_key_pt_anchor = len(list_double_region_distance_anchor)
    if num_key_pt_meas == 0 or num_key_pt_anchor == 0:
        return list_mapping_info

    for i in num_key_pt_meas:
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
        mapping_info.dist_meas_s = dist_meas_s
        mapping_info.dist_meas_e = dist_meas_e
        mapping_info.ratio_meas_to_anchor = dist_len_anchor / dist_len_meas
        mapping_info.offset_meas_to_anchor = dist_anchor_s - dist_meas_s
        list_mapping_info.append(mapping_info)
    return list_mapping_info