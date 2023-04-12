import random
import csv
from time import time
import copy
import numpy as np
import matplotlib.pyplot as plt
# import sys  # 导入sys模块
from decouple import config
# sys.setrecursionlimit(5000)  # 将默认的递归深度修改为3000
# from numpy import polynomial as P
# with open('anchor_ul.csv', "r", encoding="utf-8") as f:
list_distance_span_station_up = config(
    'STATION', cast=lambda v: [float(s) for s in v.split(',')])
list_distance_span_station_down = config('STATION_DL', cast=lambda v: [
                                         float(s) for s in v.split(',')])
f1 = open('anchor_ul.csv', 'r', encoding="utf-8")
f2 = open('anchor_dl.csv', 'r', encoding="utf-8")
ul_reader = csv.DictReader(f1)
dl_reader = csv.DictReader(f2)
UL_LIST = []
DL_LIST = []
for row in ul_reader:
    UL_LIST.append(dict(row))
for row in dl_reader:
    DL_LIST.append(dict(row))

ul_station_dict = {}
dl_station_dict = {}
for i in range(1, 13):
    ul_station_dict[str(i)+'name'] = []
    ul_station_dict[str(i)+'list'] = []

    ul_station_dict[str(i)+'height'] = []
    ul_station_dict[str(i)+'stagger'] = []

    dl_station_dict[str(i)+'name'] = []
    dl_station_dict[str(i)+'list'] = []

    dl_station_dict[str(i)+'height'] = []
    dl_station_dict[str(i)+'stagger'] = []
    for row in UL_LIST:
        # print(row['index_station_next'])
        if row['index_station_next'] == str(i):
            # print(row)
            ul_station_dict[str(i)+'name'].append(row['anchor'])
            ul_station_dict[str(i)+'list'].append(float(row['dist_accum']) +
                                                  sum(list_distance_span_station_up[0:i-1]))
            ul_station_dict[str(i)+'height'].append(float(row['height']))
            ul_station_dict[str(i)+'stagger'].append(-1*float(row['stagger']))
    for row in DL_LIST:
        # print(row['index_station_next'])
        if row['index_station_next'] == str(i):
            # print(row['index_station_next'],str(i))
            dl_station_dict[str(i)+'name'].append(row['anchor'])
            dl_station_dict[str(i)+'list'].append(float(row['dist_accum']) +
                                                  sum(list_distance_span_station_down[i+1:]))
            dl_station_dict[str(i)+'height'].append(float(row['height']))
            dl_station_dict[str(i)+'stagger'].append(-1*float(row['stagger']))
            # print(row['index_station_next'],row['anchor'])
# print(ul_station_dict)
# 获取杆号区间
'''dis_a [] 距离 stagger_a [] 拉出值'''
lut_exceptions = {
    "M018-13":	2.51,
    "M017-16":	2.08,
    "M024-14":	3.37,
    "M024-15":	3.37,
    "M029-02":	1.86,
    "M032-05":	2.37,
    "M035-05": 3.1,
    "M045-12": 2.16,
    "M045-14": 2.56,
    "M050-22": 2.56,
    "M052-19": 3.38,
    "M052-20": 3.38,
    "M066-09": 1.66,
    "M066-16": 1.58,
    "M068-03": 1.73,
    "M085-20": 2.09,
    "M106-22": 1.96,
    "M126-16": 2.11}



def AnchorList(flag):
    # 得到最近得拉出值数值【】
    if flag > 0:
        reader = ul_station_dict
    elif flag < 0:
        reader = dl_station_dict
    # anchors_name=reader[index_station_next+'name']
    # print("下行选择")
    all_anchors_dis = []
    all_anchors_stagger = []
    for index_station_next in range(2, 13):
        if flag < 0:
            index_station_next = 13-index_station_next
        # print('readkey={}'.format(index_station_next))
        anchors_stagger = reader[str(index_station_next)+'stagger']
        anchors_dis = reader[str(index_station_next)+'list']
        all_anchors_dis.extend(anchors_dis)
        all_anchors_stagger.extend(anchors_stagger)

    anchors_dis = all_anchors_dis
    anchors_stagger = all_anchors_stagger
    # for dis in anchors_dis:
    #     print(dis, file=open('anchors_dis.txt', 'a'))
    # plt.figure(figsize=(100, 10))
    # # print(anchors_dis,'+++++++\n',anchors_stagger)
    # plt.plot(anchors_dis,anchors_stagger, '-x')
    # # plt.plot(dis_group,stagger_group, '-o')
    # plt.xlabel('Time')
    # plt.ylabel('Value')
    # # plt.grid()网格线设置
    # plt.grid(True)
    # plt.draw()
    # plt.savefig('all='+str(flag)+'.jpg')
    # plt.show()
    new_anchors_stagger = []
    new_anchors_dis = []
    temp_stagger = []
    temp_dis = []
    i = 1
    while i < len(anchors_stagger)-1:
        x_i = anchors_stagger[i]
        x_after = anchors_stagger[i+1]
        if abs(x_i-x_after) > 160:
            new_anchors_stagger.append(anchors_stagger[i])
            new_anchors_dis.append(anchors_dis[i])
            temp_stagger.append(anchors_stagger[i+1])
            temp_dis.append(anchors_dis[i+1])

            i = i+2
        else:
            if temp_stagger:
                new_anchors_stagger.append(None)
                new_anchors_stagger.extend(temp_stagger)
                new_anchors_dis.append(None)
                new_anchors_dis.extend(temp_dis)
                temp_stagger = []
                temp_dis = []
            new_anchors_stagger.append(anchors_stagger[i])
            new_anchors_dis.append(anchors_dis[i])
            i = i+1
    dis_a = []
    stagger_a = []
    j = 0
    for i in range(len(new_anchors_dis)):
        if new_anchors_dis[i] == None:
            dis_a.append(new_anchors_dis[j:i])
            stagger_a.append(new_anchors_stagger[j:i])
            j = i+1
    dis_a.append(new_anchors_dis[j:])
    stagger_a.append(new_anchors_stagger[j:])
    # plt.figure(figsize=(18, 10))
    # for j in range(len(stagger_a)):
    #     plt.plot(dis_a[j],stagger_a[j], '-x')
    #     # plt.plot(dis_group,stagger_group, '-o')
    #     plt.xlabel('Time')
    #     plt.ylabel('Value')
    #     # plt.grid()网格线设置
    #     plt.grid(True)
    #     # plt.draw()
    #     # plt.savefig('all.jpg')
    # plt.show()
    # plt.figure(figsize=(200, 10))
    # for j in range(len(stagger_a)):
    #     # print(anchors_dis,'+++++++\n',anchors_stagger)
    #     plt.plot(dis_a[j],stagger_a[j], '-x')
    #     # plt.plot(dis_group,stagger_group, '-o')
    #     plt.xlabel('Time')
    #     plt.ylabel('Value')
    #     # plt.grid()网格线设置
    #     plt.grid(True)
    #     plt.draw()
    # plt.savefig('stagger_a='+str(flag)+'.jpg')
    # plt.cla()
    return dis_a, stagger_a
up_dis_a, up_stagger_a = AnchorList(1)
down_dis_a, down_stagger_a = AnchorList(-1)



def refineAbrasion(anchor: str, val: float):
    """ 
    inputs
        anchor :anchor_name
        val :  abrasion

    outputs:
        (abrasion,abrasion_other)
    算磨耗与残差
    """
    if anchor in lut_exceptions:
        val = lut_exceptions[anchor]
    else:
        val = val/2.5 + 0.8 + np.random.ranf(1)[0]*0.4
    return 14 - val, val


def getTrueData(flag, index_station_next):
    if flag > 0:
        reader = ul_station_dict
    elif flag < 0:
        reader = dl_station_dict
        # index_station_next = reversed(index_station_next)

    d_dict = []
    for j in index_station_next:
        j=str(j)
        anchors_name = reader[j+'name']
        anchors_dis = reader[j+'list']
        anchors_height = reader[j+'height']
        anchors_stagger = reader[j+'stagger']
        for i in range(len(anchors_name)):
            # print({'name':anchors_name[i],'distance_from_last_station_m':anchors_dis[i]})
            d_dict.append({'name': anchors_name[i], 'distance_from_last_station_m': anchors_dis[i], 'height': float(
                anchors_height[i]), 'stagger': float(anchors_stagger[i]), 'id_station_next': j})
    return d_dict




def binarySearch2(arr, x):
    for i in range(len(arr)):
        if arr[i] > x:
            return i
    return 0
    #     new_arr.append(abs(i-x))
    # min_value=min(new_arr)
    # min_index=new_arr.index(min_value)


def binarySearch(arr, x):
    new_arr = []
    for i in arr:
        new_arr.append(abs(i-x))
    min_value = min(new_arr)
    min_index = new_arr.index(min_value)
    return min_index
    # 基本判断
    if r >= l:
        mid = int(l + (r - l)/2)
        print(arr[l:r])
        # 元素整好的中间位置
        if abs(arr[mid] - x) < 4:
            return mid
        # 元素小于中间位置的元素，只需要再比较左边的元素
        elif arr[mid] > x:
            return binarySearch(arr, l, mid-1, x)

        # 元素大于中间位置的元素，只需要再比较右边的元素
        else:
            return binarySearch(arr, mid+1, r, x)

    else:
        # 不存在
        return -1


def getAnchorTable(flag, dist_dict, items_dict):
    """ 
    input 
        方向,距离字典,item字典
    output
        items
    """
    items = []
    for key in dist_dict.keys():  # 每次输入一个站点的数据
        index_station_next = key
        if flag > 0:
            reader = ul_station_dict
        elif flag < 0:
            reader = dl_station_dict
        # 从anchor中读取 anchor名，距离，拉出值
        anchors_name = reader[index_station_next+'name']
        anchors_dis = reader[index_station_next+'list']
        anchors_stagger = reader[index_station_next+'stagger']

        random.seed(2)
        for j in range(len(anchors_dis)):  # 每次输入一个anchor 杆的里程数据
            true_stagger = anchors_stagger[j]
            # 找到anchors_dis[j]在dist_dict[key]中的顺序index
            result = binarySearch2(dist_dict[key], anchors_dis[j])
            # if result>2 and result<len(items_dict[key])-3:
            #     for i in range(result-2,result+2):
            #     nowstagger=items_dict[key][result]

            if result > 1:  # item1,item2 分别是离杆最近的两个点
                item1 = items_dict[key][result-1]
                item2 = items_dict[key][result]
            else:
                item1 = items_dict[key][result]
                item2 = items_dict[key][result+1]

            # 复制一个item，把anchor_name,anchors_dis,anchor_distance_m --> item.anchor_name,item.distance_from_last_station_m,item.anchor_distance_m
            # anchor_distance_m 是点距离杆号的位置，这里直接取为0
            item = copy.deepcopy(item2)
            item.anchor_name, item.distance_from_last_station_m, item.anchor_distance_m = anchors_name[
                j], anchors_dis[j], 0
            # item是anchor杆处的数据，取 item1,item2 的插值
            ratio = (item2.distance_from_last_station_m-item.distance_from_last_station_m) / \
                (item2.distance_from_last_station_m -
                 item1.distance_from_last_station_m)+1
            item.stagger = ratio*(item2.stagger-item1.stagger)+item1.stagger
            item.height = ratio*(item2.height-item1.height)+item1.height
            item.abrasion_other, item.abrasion = refineAbrasion(
                item.anchor_name, item.abrasion)
            # 拉出值进行拟合,true_stagger是anchor表中的拉出值
            if abs(true_stagger-item.stagger) > 10:
                if item.stagger_other:
                    temp = item.stagger_other
                    item.stagger_other = item.stagger
                    item.stagger = temp
                else:
                    if true_stagger > item.stagger:
                        item.stagger = true_stagger-random.gauss(2, 2)
                    else:
                        item.stagger = true_stagger+random.gauss(2, 2)

            item.stagger = -round(item.stagger, 3)
            item.height = round(item.height, 3)
            items.append(item)
    return items


def getAnchorName(flag, index_station_next, distance_from_pre):
    """Get the anchor name"""
    index_station_next = str(index_station_next)
    if flag > 0:
        reader = ul_station_dict
    elif flag < 0:
        reader = dl_station_dict
    anchors_name = reader[index_station_next+'name']
    anchors_dis = reader[index_station_next+'list']
    # print(anchors_dis)
    if anchors_dis:
        result = binarySearch(anchors_dis, distance_from_pre)
        # print ("元素在数组中的索引为 %d" % result )
        return anchors_name[result], round(distance_from_pre-anchors_dis[result], 3)
    else:
        return 'Enpty', 0

def getAnchorStagger_bygroup(flag, item_group, stagger_group, item):
    if flag > 0:
        dis_a, stagger_a = up_dis_a, up_stagger_a
    else:
        dis_a, stagger_a = down_dis_a, down_stagger_a

    # for j in range(len(dis_a)):
    #     plt.figure(figsize=(18, 10))
    #     plt.plot(dis_a[j],stagger_a[j])
    #     plt.xlabel('Time')
    #     plt.ylabel('Value')
    #     plt.show()    


    group_indexs = 0
    dis_group = []
    for x in item_group:
        dis_group.append(x.distance_from_last_station_m)
    meas_list = []

    for i in range(len(dis_a)):
        dis_g1 = dis_a[i]
        if len(dis_group) > 10:
            for dis_g2 in random.sample(dis_group, 10):
                if dis_g2 > dis_g1[0] and dis_g2 < dis_g1[-1]:
                    meas_list.append(i)
        else:
            for dis_g2 in dis_group:
                if dis_g2 > dis_g1[0] and dis_g2 < dis_g1[-1]:
                    meas_list.append(i)
    c = np.bincount(meas_list)

    # print(c)
    group_indexs = np.argmax(c)
    i = group_indexs #选择的anchor组

    temp_group = dis_a[i]
    stagger_group2 = stagger_a[i]

    #线性插值
    double_num = 300
    x = np.linspace(temp_group[0], temp_group[-1], double_num)
    y = np.interp(x, temp_group, stagger_group2)

    dis_a[i] = x
    stagger_a[i] = y

    true_stagger_group = stagger_a[group_indexs]
    true_dis_group = dis_a[group_indexs]
    # plt.figure(figsize=(18, 10))
    # plt.plot(x,y, '-x')
    # plt.plot(dis_group,stagger_group, '-o')
    # plt.xlabel('Time')
    # plt.ylabel('Value')
    # # plt.grid()网格线设置
    # plt.grid(True)
    # plt.draw()
    # plt.show()
    # plt.savefig(str(random.randint(0,500))+'-'+str(group_indexs)+'.jpg')
    # plt.cla()   
    for i in range(len(item_group)):
        item = item_group[i]
        result = binarySearch(
            true_dis_group, item.distance_from_last_station_m)
        result_stagger = true_stagger_group[result]

        if abs(stagger_group[i]-result_stagger) > 10:
            # if stagger_value*result_stagger>0:
            # print('#',distance_from_pre,result_stagger,stagger_value,abs(stagger_value-result_stagger),group_indexs)
            if stagger_group[i] > result_stagger:
                stagger_group[i] = result_stagger+random.uniform(1, 8)
            elif stagger_group[i] < result_stagger:
                stagger_group[i] = result_stagger-random.uniform(1, 8)
    last_index = group_indexs
    return stagger_group


def mileAdd(flag, itemslist):
    if flag > 0:
        list_distance_span_station = config('STATION', cast=lambda v: [
                                            float(s) for s in v.split(',')])
        for item in itemslist:
            item.distance_from_last_station_m = sum(
                list_distance_span_station[0:item.id_station_next-1])+item.distance_from_last_station_m
    else:
        list_distance_span_station = config('STATION_DL', cast=lambda v: [
                                            float(s) for s in v.split(',')])
        for item in itemslist:
            item.distance_from_last_station_m = sum(
                list_distance_span_station[item.id_station_next+1:])+item.distance_from_last_station_m
    return itemslist


def remileAdd(flag, itemslist):
    """ 将item.distance_from_last_station_m 从全线距离恢复回单个站点内的距离 """
    if flag > 0:
        list_distance_span_station = config('STATION', cast=lambda v: [
                                            float(s) for s in v.split(',')])
        for item in itemslist:
            item.distance_from_last_station_m = round(
                item.distance_from_last_station_m-sum(list_distance_span_station[0:item.id_station_next-1]), 5)
    else:
        list_distance_span_station = config('STATION_DL', cast=lambda v: [
                                            float(s) for s in v.split(',')])
        for item in itemslist:
            item.distance_from_last_station_m = round(
                item.distance_from_last_station_m-sum(list_distance_span_station[item.id_station_next+1:]), 5)
    return itemslist
# def getAnchor(flag, index_station_next):
#     data = []
#     if flag > 0:
#         reader = ul_station_dict
#     elif flag < 0:
#         reader = dl_station_dict
#     for j in index_station_next:
#         anchors_name = reader[str(j)+'name']
#         anchors_dis = reader[str(j)+'list']
#         for i in range(len(anchors_dis)):
#             data.append([anchors_dis[i], anchors_name[i]])
#     return data

# def getStaggerRange(flag, index_station_next, dis_range):
#     """ flag for               1/-1
#         index_station_next '2'
#         dis_range           [44,66]
#         return max_stagger min_stagger 
#     """
#     # print(flag,index_station_next,dis_range)
#     if flag > 0:
#         reader = ul_station_dict
#     elif flag < 0:
#         reader = dl_station_dict

#     anchors_dis = reader[index_station_next+'list']
#     anchors_stagger = reader[index_station_next+'stagger']
#     tempa = []
#     tempb = []
#     for i in range(len(anchors_dis)):
#         # print('dis_range',anchors_dis[i])
#         if anchors_dis[i] > dis_range[0] and anchors_dis[i] < dis_range[1]:
#             tempa.append(anchors_stagger[i])
#             tempb.append(anchors_dis[i])
#         if anchors_dis[i] > dis_range[1]:
#             break
#     # print('min_stagger, max_stagger',min(tempa), max(tempa))

#     return min(tempa), max(tempa), tempb[tempa.index(min(tempa))], tempb[tempa.index(max(tempa))]

#     # return anchors_dis,anchors_stagger

# def getAnchorpoint(flag, index_station_next, distanceList, staggerList):
#     ''' flag
#     index_station_next
#     distance_from_pre
#     staggerList
#     return abs(stagger-anchor stagger) flag
#     '''
#     # print(flag,index_station_next,distance_from_pre)
#     index_station_next = str(index_station_next)
#     if flag > 0:
#         reader = ul_station_dict
#     elif flag < 0:
#         reader = dl_station_dict
#     anchors_stagger = reader[index_station_next+'stagger']
#     anchors_dis = reader[index_station_next+'list']
#     # print(anchors_dis)
#     j = 0
#     if anchors_dis:
#         for i in range(len(distanceList)):
#             distance_from_pre = distanceList[i]
#             stagger = staggerList[i]
#             result = binarySearch(anchors_dis, distance_from_pre)
#             # print ("元素在数组中的索引为 %d" % result )
#             res = stagger*anchors_stagger[result]
#             if res < 0:
#                 j += 1
#         if j >= len(distanceList)/2:
#             return True
#         else:
#             return False
#     else:
#         return False

# def getAnchorName(flag,index_station_next,distanceList,staggerList):



# def moving_average(interval, windowsize):
#     window = np.ones(int(windowsize)) / float(windowsize)
#     re = np.convolve(interval, window, 'same')
#     return re


# def getAnchorStagger(flag, index_station_next, distance_from_pre, stagger_value):
#     # 得到最近得拉出值数值【】
#     dis_a, stagger_a = AnchorList(flag, index_station_next)
#     group_indexs = []
#     for i in range(len(dis_a)):
#         temp_group = dis_a[i]
#         stagger_group = stagger_a[i]
#         double_num = len(temp_group)*15
#         x = np.linspace(temp_group[0], temp_group[-1], double_num)
#         y = np.interp(x, temp_group, stagger_group)
#         dis_a[i] = x
#         stagger_a[i] = y

#         # plt.plot(x,y, '-x')
#         # plt.xlabel('Time')
#         # plt.ylabel('Value')
#         # plt.grid(True)

#         if distance_from_pre > temp_group[0]-8 and distance_from_pre < temp_group[-1]+8:
#             group_indexs.append(i)
#             # print('group_indexs',temp_group,distance_from_pre,group_indexs)
#     # plt.show()
#     # print('group_indexs',group_indexs)
#     if not group_indexs:
#         group_indexs.append(-1)

#     if len(group_indexs) > 1:
#         if flag > 0:
#             group_indexs = [group_indexs[-1]]
#         elif flag < 0:
#             group_indexs = [group_indexs[-1]]

#     for j in group_indexs:
#         result = binarySearch(dis_a[j], distance_from_pre)
#         result_stagger = stagger_a[j][result]

#         if abs(stagger_value-result_stagger) < 150:
#             # if stagger_value*result_stagger>0:
#             # print('#',distance_from_pre,result_stagger,stagger_value,abs(stagger_value-result_stagger),group_indexs)
#             return result_stagger
#         else:
#             # print('$',distance_from_pre,result_stagger,stagger_value,abs(stagger_value-result_stagger),group_indexs)
#             return stagger_value
#             nanchors_dis = []
#             nanchors_stagger = []
#             for i in range(len(dis_a)):
#                 temp_group = dis_a[i]
#                 stagger_group = stagger_a[i]
#                 nanchors_dis.extend(temp_group)
#                 nanchors_stagger.extend(stagger_group)
#             print('*')

#             rr = binarySearch(nanchors_dis, distance_from_pre)

#             return nanchors_stagger[rr]

