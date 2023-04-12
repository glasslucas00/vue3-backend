import numpy as np
# import matplotlib.pyplot as plt

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def timer(func):
    def func_wrapper(*args, **kwargs):
        from time import time
        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_spend = time_end - time_start
        print('%s cost time: %.3f s' % (func.__name__, time_spend))
        return result
    return func_wrapper

def findNearest(list_val, target, index_search_start = 0):
    diff_min = None
    index_min = None
    for i in range(index_search_start, len(list_val)):
        val = list_val[i]
        diff = abs(target - val)

        if diff_min is None:
            diff_min = diff
            index_min = i
            continue
        
        if diff < diff_min:
            diff_min = diff
            index_min = i
            continue
        if diff > diff_min:
            break
    return index_min


class Anchor(object):
    def __init__(self) -> None:
        self.anchor = None
        self.seg = 0
        self.station_next_name = None
        self.index_station_next = 0
        self.dist_from_span = 0
        self.height = None
        self.stagger = None
        self.flag_double_region = False

    def print(self):
        print(f'{self.index_station_next},{self.anchor},{self.dist_from_span}')


MIN_DIST_DIFF = 2
MIN_INTERVAL = 15
class AnchorsInStation(object):
    def __init__(self, index_station_next) -> None:
        self.list_dist = list()
        self.list_anchors = list()
        self.index_station_next = index_station_next
        self.list_kp = list()
        self.list_double_region_start_index = list()

    def addAnchor(self, anchor):
        if len(self.list_dist) > 0:
            dist_diff = anchor.dist_from_span - self.list_dist[-1]
            if dist_diff < MIN_DIST_DIFF:
                anchor.flag_double_region = True
                self.list_anchors[-1].flag_double_region = True
        self.list_anchors.append(anchor)
        self.list_dist.append(anchor.dist_from_span)

    def finalAnalysis(self):
        self.list_kp = list()
        self.list_double_region_start_index = list()
        for i in range(len(self.list_anchors)):
            if not self.list_anchors[i].flag_double_region:
                continue
            # check if previous anchor is not
            if i > 0 and self.list_anchors[i-1].flag_double_region:
                continue

            dist_this = self.list_dist[i]
            # check if last double region too near
            if len(self.list_kp) > 1 and (dist_this - self.list_kp[-1] < MIN_INTERVAL):
                continue
            self.list_kp.append(self.list_dist[i]) 
            self.list_double_region_start_index.append(i)


    def getListDist(self):
        return np.asarray(self.list_dist)

    def getAnchor(self, index):
        return self.list_anchors[index]

    def print(self):
        print(f'-----{self.index_station_next}-----')
        for item in self.list_anchors:
            item.print()

    def getGeoData(self):
        list_dist = list()
        list_stagger = list()
        list_dist_diff = list()
        for i in range(len(self.list_dist)):
            list_dist.append(self.list_dist[i])
            list_stagger.append(self.list_anchors[i].stagger)
            if i == len(self.list_dist)-1:
                list_dist_diff.append( self.list_dist[i] - self.list_dist[i-1] )
            else:
                list_dist_diff.append( self.list_dist[i+1] - self.list_dist[i] )
        return list_dist, list_stagger, list_dist_diff, self.list_kp
        
class Anchors(object):
    def __init__(self) -> None:
        self.lut_station_anchors_ul = dict()
        self.lut_station_anchors_dl = dict()
        self.DoubleRegionDict={}
    def loadALL(self, file_ul, file_dl):
        self.loadCSV(file_ul, self.lut_station_anchors_ul)
        self.loadCSV(file_dl, self.lut_station_anchors_dl)

    def loadCSV(self, file_csv, lut):
        lut.clear()
        with open(file_csv, 'r', encoding='utf-8') as f:
            line = f.readline()
            for line in f:
                list_str = line.split(',')
                if len(list_str) < 6:
                    continue
                # print(list_str)
                anchor = Anchor()
                anchor.anchor = list_str[0]
                anchor.index_station_next = int(list_str[1])
                anchor.station_next_name = list_str[2]
                anchor.dist_from_span = float(list_str[3])

                if is_number(list_str[4]):
                    anchor.height = float(list_str[4])
                else:
                    anchor.height = 0

                if is_number(list_str[5]):
                    anchor.stagger = float(list_str[5])
                else:
                    anchor.stagger = 0
                if abs(anchor.stagger) > 500:
                    print(line)

                if anchor.index_station_next not in lut:
                    lut[anchor.index_station_next] = AnchorsInStation(anchor.index_station_next)
                lut[anchor.index_station_next].addAnchor(anchor)
        self.finalAnalysis(lut)

    def finalAnalysis(self, dict_anchors):
        for key in dict_anchors:
            dict_anchors[key].finalAnalysis()
           

    def getListNextStation(self, flag_ul_or_dl):
        lut = self.lut_station_anchors_ul if flag_ul_or_dl else self.lut_station_anchors_dl 
        return list(lut.keys())

    def getGeoData(self, dict_anchors, list_id_station_next_selected = list()):
        list_dist_all = list()
        list_stagger_all = list()
        list_dist_diff_all = list()
        list_dist_kp_all = list()
        list_dist_station_start_all = list()
        list_id_station_next_all = list()

        list_station = list(dict_anchors.keys())
        dist_preall = 0
        for i in range(len(list_station)):
            key = list_station[i]

            if len(list_id_station_next_selected) != 0:
                if key not in list_id_station_next_selected:
                    continue

            list_id_station_next_all.append(key)
            list_dist, list_stagger, list_dist_diff, list_dist_kp = dict_anchors[key].getGeoData()
            if key not in self.DoubleRegionDict.keys():
                self.DoubleRegionDict[key]=[]
            self.DoubleRegionDict[key]=list_dist_kp
            print('anchor double key',key,self.DoubleRegionDict[key])
            list_dist_all += list(np.asarray(list_dist) + dist_preall)
            list_dist_kp_all += list(np.asarray(list_dist_kp) + dist_preall)
            list_dist_diff_all += list_dist_diff
            list_stagger_all += list_stagger
            list_dist_station_start_all.append(dist_preall)
            # dist_preall = list_dist_all[-1]
    
        return list_dist_all, list_stagger_all, list_dist_diff_all, list_dist_kp_all, list_dist_station_start_all, list_id_station_next_all

    def plot(self, flag_ul_or_dl, list_id_station_next_selected = list()):
        lut = self.lut_station_anchors_ul if flag_ul_or_dl else self.lut_station_anchors_dl
        list_dist, list_stagger, list_dist_diff, list_dist_kp, list_dist_station_start, list_id_station_next = self.getGeoData(lut, list_id_station_next_selected)
        # plt.figure()
        return None
        # figure, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        # ax1.plot(list_dist, list_stagger)
        # ax1.set_ylabel('stagger')
        # for dist in list_dist_kp:
        #     ax1.plot([dist, dist], [-300, 300], 'r')
        # for i in range(len(list_dist_station_start)):
        #     dist = list_dist_station_start[i]
        #     id_station_next = list_id_station_next[i]
        #     ax1.plot([dist, dist], [-400, 400], 'g', linestyle='dashed')
        #     ax1.annotate(text=f'#{id_station_next}',  xytext=(dist+10, 500), xy=(dist, 350), arrowprops=dict(arrowstyle="<-"))
        # # plt.subplot(2, 1, 2)
        # ax2.set_ylabel('dist diff to prev')
        # ax2.plot(list_dist, list_dist_diff)
        # for dist in list_dist_kp:
        #     ax2.plot([dist, dist], [5, 10], 'r')
        # for dist in list_dist_station_start:
        #     ax2.plot([dist, dist], [4, 8], 'g', linestyle='dashed')
        # plt.show()

    def plotAll(self):
        self.plot(True)
        self.plot(False)

    def getAnchors(self, flag_ul_or_dl, list_index_station_next):
        list_anchors = list()
        stations=[int(list_index_station_next[0]),int(list_index_station_next[1])]
        if int(flag_ul_or_dl)>0:
            stations=[int(list_index_station_next[0])+1,int(list_index_station_next[1])+1]


        for i in range(stations[0],stations[1]):
            anchors_in_station = self.__getAnchorsInStation(flag_ul_or_dl, i)
            print(i,anchors_in_station)
            if anchors_in_station is None:
                continue
            list_anchors.append(anchors_in_station)
        return list_anchors

    def findNearset(self, flag_ul_or_dl, index_station_next, list_dist_input):
        list_anchor_name = list()# 最近杆号
        list_anchor_dist_offset = list()# 最近杆号距离
    
        anchors_in_station = self.__getAnchorsInStation(flag_ul_or_dl, index_station_next)
        if anchors_in_station is None:
            return list_anchor_name, list_anchor_dist_offset
        list_dist_anchor = anchors_in_station.getListDist()

        index_nearest = 0
        for i in range(len(list_dist_input)):
            dist = list_dist_input[i]
            index_nearest = findNearest(list_dist_anchor, dist, index_nearest)
            anchor = anchors_in_station.getAnchor(index_nearest)
            list_anchor_name.append( anchor.anchor )
            list_anchor_dist_offset.append( anchor.dist_from_span - dist )
        return list_anchor_name, list_anchor_dist_offset

    def __getAnchorsInStation(self, flag_ul_or_dl, index_station_next):
        if int(flag_ul_or_dl)==1:
            if index_station_next not in self.lut_station_anchors_ul:
                return None
            return self.lut_station_anchors_ul[index_station_next]
        elif int(flag_ul_or_dl)==-1:
            if index_station_next not in self.lut_station_anchors_dl:
                return None
            return self.lut_station_anchors_dl[index_station_next]
        else:
            return None

    def print(self):
        for station in self.lut_station_anchors_dl:
            self.lut_station_anchors_dl[station].print()
        for station in self.lut_station_anchors_ul:
            self.lut_station_anchors_ul[station].print()



def testFindNearest():
    list_val = [0,1,2,3,4,5,6,7,8]
    index_nearest = findNearest(list_val, 2.2)
    print(f"2.2, findNearest:{index_nearest}")

    index_nearest = findNearest(list_val, 7.8)
    print(f"7.8 findNearest:{index_nearest}")

 
def testSearchTable(flag,index_station_next,list_dist_dummy):
    # print(flag,index_station_next,list_dist_dummy)
    anchors = Anchors()
    anchors.loadALL('anchor_ul.csv', 'anchor_dl.csv')
    # anchors.print()
    
    # 模拟一个距离数组, 上行，开往第7个站，100个距离点位求最近杆号
    # index_station_next = 7
    # list_dist_dummy = [1.2]
    # for i in range(100):
    #     list_dist_dummy.append(1.2*i)
    # print(flag, index_station_next, list_dist_dummy)

    # if not is_number(flag):
    #     flag = eval(flag)
    # if not is_number(index_station_next):
    #     index_station_next = eval(index_station_next)
    # if not is_number(list_dist_dummy[0]):
    #     list_dist_dummy[0]= int(list_dist_dummy[0])
    if isinstance(flag,str):
        flag = eval(flag)
    if isinstance(index_station_next,str):
        index_station_next = eval(index_station_next) 
    if isinstance(list_dist_dummy[0],str):
         list_dist_dummy[0]= int(list_dist_dummy[0])


    list_anchor_name, list_anchor_dist_offset = anchors.findNearset(flag, index_station_next, list_dist_dummy)
    # print(list_anchor_name)
    if list_anchor_name:
        return list_anchor_name[0], round(list_anchor_dist_offset[0],3)
    else:
        return None, None
    for i in range(len(list_anchor_name)):
        print(f'第{i}个数据，距离{list_dist_dummy[i]:.2f},最近杆号{list_anchor_name[i]}, 距离最近杆号距离{list_anchor_dist_offset[i]:.2f}')

@timer
def testSearchPlot(flag,list_index_station_next):
    anchors = Anchors()
    anchors.loadALL('anchor_ul.csv', 'anchor_dl.csv')
    # anchors.print()
    from decouple import config
    if int(flag)==1:
        list_distance_span_station =config('STATION', cast=lambda v: [float(s) for s in v.split(',')])
        anchors.plot(True)
    else:
        list_distance_span_station =config('STATION_DL', cast=lambda v: [float(s) for s in v.split(',')])
        anchors.plot(False)

    # 模拟一个距离数组, 上行，开往第7个站，100个距离点位求最近杆号
    # 1~5
    # 得到每个区间的长度
    # 1->2: 2， 2.3km
    # 2->3: 3, 1.8km
    # 3->4: 4, 2.4km
    # 4->5: 5, 6.1km

    # list_distance_span_station = [0,0, 0, 0, 1605,1209,1082,1130,3313,1224,1546,1552]# table up
    # list_distance_span_station = [0,0, 0, 0, 1605,1209,1082,1130,3313,1224,1546,1552]# table down

    # list_distance_span_station=[0,0,0,0,1628.88,1230.61,1100.52,1144.48,1442.72,1926.28,1898.7,4839.12,0,0,0,0] #database
    # list_distance_span_station = [0,0, 0, 0, 1628.88,1230.61,1100.52,1144.48,3313,1926.28,1898.7,4839.12]# max(table  ,database) 

    list_dist_total = list()
    # flag=True
    # list_index_station_next = [5,6,7,8] #输入区间
    list_anchors = anchors.getAnchors(flag, list_index_station_next)
    anchors_list_total=[]

    for i in range(len(list_anchors)):
        anchors_in_one_station = list_anchors[i]
        print(f'下一站开往:{anchors_in_one_station.index_station_next}')
        # print(f'下一站开往:{anchors_in_one_station.list_dist}')
        # print(anchors_in_one_station.getAnchor(1).anchor)
      
        # dist_from_origin = list_distance_span_station[i]
        if int(flag)==1:
            dist_from_origin = sum(list_distance_span_station[:anchors_in_one_station.index_station_next-1])
        else:
            dist_from_origin = sum(list_distance_span_station[anchors_in_one_station.index_station_next+1:])
            # print('8888',anchors_in_one_station.index_station_next,list_distance_span_station[anchors_in_one_station.index_station_next+1:])
        # print(dist_from_origin,list_distance_span_station[:anchors_in_one_station.index_station_next-1])
        for anchor in anchors_in_one_station.list_anchors:
            # print(anchors.anchor)
            anchors_list_total.append(anchor.anchor)
        for dist in anchors_in_one_station.getListDist():
            # print(dist_from_origin,dist,'\n')
            list_dist_total.append(dist_from_origin + dist)
        # print(list_dist_total)
        # print(len(anchors_list_total))
    new_set=[]
    for i in range(len(list_dist_total)):
        new_set.append([list_dist_total[i],anchors_list_total[i]])
    # print(new_set)
    return new_set,anchors.DoubleRegionDict
    print(list_dist_total)
    print(anchors_list_total)

    
##########  test  ###########
# def testSearchTable2():
#     anchors = Anchors()
#     anchors.loadALL('anchor_ul.csv', 'anchor_dl.csv')
#     # anchors.print()
    
#     # 模拟一个距离数组, 上行，开往第7个站，100个距离点位求最近杆号
#     index_station_next = 11
#     list_dist_dummy = [102]
#     # for i in range(100):
#     #     list_dist_dummy.append(1.2*i)
#     list_anchor_name, list_anchor_dist_offset = anchors.findNearset(-1, index_station_next, list_dist_dummy)
#     for i in range(len(list_anchor_name)):
#         print(f'第{i}个数据，距离{list_dist_dummy[i]:.2f},最近杆号{list_anchor_name[i]}, 距离最近杆号距离{list_anchor_dist_offset[i]:.2f}')

# def testSearchPlot2():
#     anchors = Anchors()
#     anchors.loadALL('anchor_ul.csv', 'anchor_dl.csv')
#     # anchors.print()
    
#     # 模拟一个距离数组, 上行，开往第7个站，100个距离点位求最近杆号
#     # 1~5
#     # 得到每个区间的长度
#     # 1->2: 2， 2.3km
#     # 2->3: 3, 1.8km
#     # 3->4: 4, 2.4km
#     # 4->5: 5, 6.1km
#     # list_distance_span_station = [2300, 1200, 1500, 3000]# [0, 2300, 1200, 1500, 3000] 
#     list_distance_span_station = [0,2300, 1200, 1500, 3000,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200]
#     list_dist_total = list()


#     list_index_station_next = [5,6] #输入区间
#     list_anchors = anchors.getAnchors(True, list_index_station_next)
#     anchors_list_total=[]
#     for i in range(len(list_anchors)):
#         anchors_in_one_station = list_anchors[i]
#         print(f'下一站开往:{anchors_in_one_station.index_station_next}')
#         # print(f'下一站开往:{anchors_in_one_station.list_dist}')
#         # print(anchors_in_one_station.getAnchor(1).anchor)
      
#         dist_from_origin = list_distance_span_station[i]
#         for anchor in anchors_in_one_station.list_anchors:
#             # print(anchors.anchor)
#             anchors_list_total.append(anchor.anchor)
#         for dist in anchors_in_one_station.getListDist():
#             list_dist_total.append(dist_from_origin + dist)
#         # print(len(list_dist_total))
#         # print(len(anchors_list_total))
#     print(list_dist_total)
#     print(anchors_list_total)
##########  test  ###########



    
if __name__ == '__main__':
    # testFindNearest()
    # testSearchTable()
    # testSearchPlot()
    # pass
    # testSearchTable2()
    # a,b=testSearchTable('-1','11',['103'])
    # print(a,b)
    # testSearchPlot(1,[5,8])

    anchors = Anchors()
    anchors.loadALL('anchor_ul.csv', 'anchor_dl.csv')
    anchors.plot(True)

