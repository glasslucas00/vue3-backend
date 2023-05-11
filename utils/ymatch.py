import numpy as np
from scipy.signal import find_peaks, argrelmin
from utils.Anchor import Anchor
# from Anchor import Anchor
# import matplotlib.pyplot as plt
import copy
from decimal import Decimal
""" 
1.数据分割  dataSplit
    items -> dist_groups, stagger_groups
    anchor-> adist_groups,astagger_groups 
2.区间匹配  groupsMatch
    return match_index
3.区间拟合 groupFit
    return fit_stagger
"""


def get_fun(p1, p2):
    """return 线性方程"""
    x1, y1 = p1
    x2, y2 = p2
    k = (y1 - y2) / (x1 - x2)
    b = y2 - k * x2
    return k, b


class AnchorYMatch(object):
    def __init__(self, station, upanchor, items=None):
        self.dist = []
        self.stagger = []
        self.station=station
        self.upanchor = upanchor
        self.dist_groups, self.stagger_groups = ([], [])
        stationInfo = upanchor.getStationInfo(station)
        self.anchor_items = upanchor.getAnchorsItems(station)
        self.aname = stationInfo['name']
        self.adist = stationInfo['dist']
        self.adist_groups, self.astagger_groups = upanchor.anchorSplit(station)
        self.match_index = []
        self.maxDist=0
        self.getData(items)

    def getData(self, items):
        for item in items:
            self.dist.append(item.distance_from_last_station_m)
            self.stagger.append(item.stagger)
        self.dist = np.array(self.dist)
        self.stagger = np.array(self.stagger)
        self.dataSplit(self.dist, self.stagger, items)

    def dataSplit(self,  dist, stagger, items=None):
        """1.数据分割"""
        for i in range(stagger.shape[0]-3):
            a = stagger[i]
            b = stagger[i+1]
            c = stagger[i+2]
            if abs(a-b) > 200 and abs(c-b) > 200:
                stagger[i+1] = (a+c)/2
        peak_indexs = []
        new_indices = []
        for i in range(stagger.shape[0]-1):
            if abs(stagger[i]-stagger[i+1]) > 150:
                new_indices.append(i+1)
                if stagger[i] > 0:
                    peak_indexs.append(i)
                else:
                    peak_indexs.append(i+1)
        self.dist_groups = np.split(dist, new_indices)
        self.stagger_groups = np.split(stagger, new_indices)
        self.item_groups = np.split(items, new_indices)
        return self.dist_groups, self.stagger_groups

    def groupsMatch(self):
        """groups in one station"""

        # 1.select the match group
        match_index = []
        for adist_group, astagger_group in zip(self.adist_groups, self.astagger_groups):
            astagger_group = np.array(astagger_group)
            adist_group = np.array(adist_group)
            if astagger_group.min() < -200:
                amiddle_position = adist_group[np.where(
                    astagger_group == astagger_group.min())][0]
            else:
                amiddle_position = (adist_group[0]+adist_group[-1]) / 2
            pmin = 80
            indexmin = -1
            for i in range(len(self.dist_groups)):
                if match_index:
                    if i <= match_index[-1] or i in match_index:
                        continue
                dist_group = np.array(self.dist_groups[i])
                stagger_group = np.array(self.stagger_groups[i])

                if stagger_group.min() < -200:
                    middle_position = dist_group[np.where(
                        stagger_group == stagger_group.min())][0]
                else:
                    middle_position = (dist_group[0]+dist_group[-1]) / 2

                if abs(amiddle_position-middle_position) < pmin:
                    pmin = abs(amiddle_position-middle_position)
                    indexmin = i
            match_index.append(indexmin)
        print('数据匹配区间选择 {}'.format(match_index))
        if -1 in match_index:
            print('Error /* 数据匹配区间选择可能错误,请检查anchor文件与数据是否匹配')
        self.match_index = match_index
        return match_index

    def groupFit(self):
        self.fit_items = [None]*self.adist.shape[0]
        # print(len(self.fit_items))
        # plt.figure(figsize=(12, 8))
        # self.staggerData = []
        # self.heightData = []
        # self.anchorStagger = []
        # self.anchorHeight = []
        # self.anchorName = []
        self.chartDatas = {'stagger':[],'height':[],'abrasion':[],'temp':[],'abrasion_other':[],'stagger_other':[],'anchorStagger':[],'anchorHeight':[],'anchorName':[]}
        # fit_stagger_groups = []
        self.sort_anchor_items = []
        for i in range(len(self.adist_groups)):
            adist_group, astagger_group = (self.adist_groups[i], self.astagger_groups[i])
            # dist_group, stagger_group = self.dataPadding(self.dist_groups[i], self.stagger_groups[i])
            g_index = self.match_index[i]
            dist_group, stagger_group = (
                self.dist_groups[g_index], self.stagger_groups[g_index])
            item_group = self.item_groups[g_index]
            # 线性插值
            double_num = 500
            x = np.linspace(dist_group[0], dist_group[-1], double_num)
            y = np.interp(x, dist_group, stagger_group)
            fit_stagger_group = []
            for (j, adist) in enumerate(adist_group):
                index = self.searchIndex(dist_group, adist)
                index2 = self.searchIndex(x, adist)

                # modifly
                t_stagger = y[index2]
                t_item = copy.deepcopy(item_group[index])
                a_stagger = astagger_group[j]
                while abs(t_stagger-a_stagger) > 10:
                    t_stagger = (t_stagger+a_stagger)/2
                t_item.stagger = round(t_stagger, 3)
                anchor_index = np.where(self.adist == adist)[0][0]
                adist+=self.maxDist
                anchor_item = self.anchor_items[anchor_index]

                t_item.anchor_name = anchor_item["name"]
                t_item.distance_from_last_station_m = adist
                t_item.abrasion, t_item.abrasion_other = self.upanchor.refineAbrasion(t_item.anchor_name, t_item.abrasion)
                fit_stagger_group.append(t_stagger)
                self.fit_items[anchor_index] = t_item

                self.chartDatas['stagger'].append([adist, t_item.stagger])
                self.chartDatas['height'].append([adist, t_item.height])
                self.chartDatas['abrasion'].append([adist, t_item.abrasion])
                self.chartDatas['temp'].append([adist, t_item.temperature_max])
                self.chartDatas['abrasion_other'].append([adist, t_item.abrasion_other])
                # self.chartDatas['stagger_other'].append([adist, t_item.stagger_other])
                self.chartDatas['anchorStagger'].append([adist, anchor_item["stagger"]])
                self.chartDatas['anchorHeight'].append([adist, anchor_item["height"]])
                self.chartDatas['anchorName'].append([adist, anchor_item["name"]])
            if i!=(len(self.adist_groups)-1):
                for key in self.chartDatas:
                    if key =="anchorName" or key =='stagger_other':
                        continue
                    self.chartDatas[key].append([adist+0.1, None])
        self.chartDatas['anchorName'].append([adist+4, '站点-'+str(self.station)])
            # fit_stagger_groups.append(fit_stagger_group)
        # print(len(self.fit_items))
        self.fit_items = self.addPointsByFit(self.fit_items)
        # self.showPlot(self.fit_items)
        return self.fit_items

    def searchIndex(self, arr, x):
        new_arr = []
        for i in arr:
            new_arr.append(abs(i-x))
        min_value = min(new_arr)
        min_index = new_arr.index(min_value)
        return min_index

    def showPlot(self, items):
        stagger = []
        dist = []
        stagger_other = []
        for item in items:
            stagger.append(item.stagger)
            stagger_other.append(item.stagger_other)
            dist.append(item.distance_from_last_station_m)

        # plt.plot(dist, stagger)
        # plt.plot(dist, stagger_other)
        # plt.show()

    def addPointsByFit(self, items):
        # plt.figure()
        """Add points by stagger lineas fit"""
        for i in range(1, len(items)-1):
            items[i].stagger_other = None
            stagger_other_front = abs(items[i].stagger-items[i+1].stagger)
            stagger_other_back = abs(items[i-1].stagger-items[i].stagger)

            if stagger_other_front > 160 and stagger_other_back > 160:
                p1 = (items[i-1].distance_from_last_station_m,
                      items[i-1].stagger)
                p2 = (items[i+1].distance_from_last_station_m,
                      items[i+1].stagger)
                # plt.plot(items[i].distance_from_last_station_m,items[i].stagger,'o')
                # plt.plot(items[i+1].distance_from_last_station_m,items[i+1].stagger,'o')
                k, b = get_fun(p1, p2)
                y = k*items[i].distance_from_last_station_m+b
                # items[i].stagger_other = Decimal(abs(items[i].stagger-y)).quantize(Decimal("0.00"))
                items[i].stagger_other = round(abs(items[i].stagger-y), 3)
            self.chartDatas['stagger_other'].append([items[i].distance_from_last_station_m, items[i].stagger_other])
        return items

# for i in range(5,10):
#     ymatch=AnchorYMatch(i)
#     dist = np.load(str(i)+'dist.npy')
#     stagger = np.load(str(i)+'stagger.npy')
#     ymatch.dataSplit(dist, stagger)
#     ymatch.groupsMatch()
#     ymatch.groupFit()


# """ 双线补点"""

# def addPointsByRandom(stagger, peak_indexs):
#     """Add points by stagger plus np.random.uniform(270, 285)"""
#     stagger_other = np.array([None]*stagger.shape[0])
#     for index in peak_indexs:
#         # left
#         if stagger[index] > 0:
#             stagger_other[index-4:index] = stagger[index -
#                                                    4:index]+np.random.uniform(270, 285)
#         else:
#             stagger_other[index:index+4] = stagger[index:index+4] + \
#                 np.random.uniform(270, 285)
#     return stagger_other


# def addPointsByFit(dist, stagger, peak_indexs):
#     """Add points by stagger lineas fit"""
#     stagger_other = np.array([None]*stagger.shape[0])
#     for index in peak_indexs:
#         # left
#         if stagger[index] > 0:
#             z1 = np.polyfit(dist[index:index+4], stagger[index:index+4], 1)
#             p1 = np.poly1d(z1)  # 得到多项式系数，按照阶数从高到低排列
#             stagger_other[index-4:index] = p1(dist[index-4:index])
#         # right
#         else:
#             z1 = np.polyfit(dist[index-4:index], stagger[index-4:index], 1)
#             p1 = np.poly1d(z1)  # 得到多项式系数，按照阶数从高到低排列
#             stagger_other[index:index+4] = p1(dist[index:index+4])
#     return stagger_other
    # def dataPadding(self,dist_group, stagger_group):
    #     """Add points by stagger lineas fit"""

    #     # plt.plot(dist_group, stagger_group, '-')
    #     sq_len = dist_group.shape[0]
    #     # frone
    #     ndist = np.arange(-10, 0)+dist_group[0]
    #     z1 = np.polyfit(dist_group[:5], stagger_group[:5], 1)
    #     if abs(z1[0]) > 20:
    #         z1 = np.polyfit(dist_group[int(sq_len/4):int(sq_len/3)],
    #                         stagger_group[int(sq_len/4):int(sq_len/3)], 1)
    #     print(z1)
    #     p1 = np.poly1d(z1)  # 得到多项式系数，按照阶数从高到低排列
    #     nstagger = p1(ndist)
    #     # plt.plot(dist_group[0:5], stagger_group[0:5], 'o')
    #     dist_group = np.concatenate((ndist, dist_group), 0)
    #     stagger_group = np.concatenate((nstagger, stagger_group), 0)
    #     # end
    #     ndist = np.arange(0, 10)+dist_group[-1]
    #     z1 = np.polyfit(dist_group[-5:], stagger_group[-5:], 1)
    #     p1 = np.poly1d(z1)  # 得到多项式系数，按照阶数从高到低排列
    #     nstagger = p1(ndist)
    #     # plt.plot(dist_group[-5:-1], stagger_group[-5:-1], '*')
    #     dist_group = np.concatenate((dist_group, ndist), 0)
    #     stagger_group = np.concatenate((stagger_group, nstagger), 0)
    #     # plt.plot(dist_group, stagger_group)

    #     return dist_group, stagger_group
