import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt


class Anchor(object):
    def __init__(self, csvfile: str):
        self.StationList = {}
        self.read(csvfile)
        self.lut_exceptions = {
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

    def read(self, csvfile: str):
        csvData = pd.read_csv(csvfile)
        csvData = csvData[:].values
        for row in csvData:
            if row[2] not in self.StationList.keys():
                self.StationList[row[2]] = {
                    'name': [], 'dist': [], 'stagger': [], 'height': []}
            self.StationList[row[2]]['name'].append(row[3])
            self.StationList[row[2]]['dist'].append(row[8])
            self.StationList[row[2]]['stagger'].append(row[5])
            self.StationList[row[2]]['height'].append(row[4])
        for key in self.StationList.keys():
            for key2 in self.StationList[key].keys():
                self.StationList[key][key2] = np.array(
                    self.StationList[key][key2])
        #     print(key,self.StationList[key]['dist'][-1])
        # print('==')
    def getStationInfo(self, station: int):
        if station in self.StationList.keys():
            return self.StationList[station]
        else:
            raise Exception(
                "/********* anchor表中无 {} 站点信息 **********/".format(station))

    def anchorSplit(self, station: int):
        stationInfo = self.StationList[station]
        dist = stationInfo['dist']
        stagger = stationInfo['stagger']
        # self.anchors_items= self.getAnchorsCharts(station)
        anchors_dis = np.append(dist, dist[-1])
        anchors_stagger = np.append(stagger, anchors_dis[-1])
        new_anchors_stagger = []
        new_anchors_dis = []
        temp_stagger = []
        temp_dis = []
        i = 0
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
        dis_a = np.array(dis_a, dtype=object)
        stagger_a = np.array(stagger_a, dtype=object)
        return dis_a, stagger_a

    def refineAbrasion(self, anchor: str, val: float):
        """ 
    inputs
        anchor :anchor_name
        val :  abrasion

    outputs:
        (abrasion,abrasion_other)
    算磨耗与残差
    """
        if anchor in self.lut_exceptions:
            val = self.lut_exceptions[anchor]
        else:
            val = val/2.5 + 0.8 + np.random.ranf(1)[0]*0.4
        val = round(val, 3)
        return 14 - val, val

    def getAnchorsItems(self, station):
        d_dict = []
        stationInfo = self.StationList[station]
        anchors_name = stationInfo['name']
        anchors_dis = stationInfo['dist']
        anchors_stagger = stationInfo['stagger']
        anchors_height = stationInfo['height']
        
        for i in range(anchors_name.shape[0]):
            d_dict.append({'name': anchors_name[i], 'distance_from_last_station_m': anchors_dis[i], 'height': float(
                anchors_height[i]), 'stagger': float(anchors_stagger[i]), 'id_station_next': station})

        return d_dict

    def getAnchorName(self, station, dist):
        try:
            stationInfo = self.StationList[station]
            anchors_name = stationInfo['name']
            anchors_dis = stationInfo['dist']
            index = self.searchIndex(anchors_dis, dist)
            anchorName = anchors_name[index]
            anchorDist = round((dist-anchors_dis[index]), 3)
            return anchorName, anchorDist
        except:
            return 'Enpty', 0

    def searchIndex(self, arr, x):
        new_arr = []
        for i in arr:
            new_arr.append(abs(i-x))
        min_value = min(new_arr)
        min_index = new_arr.index(min_value)
        return min_index
