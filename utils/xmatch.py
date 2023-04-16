import numpy as np
from scipy.signal import find_peaks
from utils.Anchor import Anchor
import matplotlib.pyplot as plt


class AnchorXMatch(object):
    def __init__(self, station, upanchor, items=None):
        self.dist = []
        self.stagger = []
        self.items = items
        self.getData(items)
        stationInfo = upanchor.getStationInfo(station)
        self.adist = stationInfo['dist']
        self.astagger = stationInfo['stagger']
        stagger = self.astagger
        dist = self.adist
        # plt.figure()
        # indices = find_peaks(stagger, height=50, threshold=None, distance=5,
        #     prominence=None, width=None, wlen=None, rel_height=None,
        #     plateau_size=None)
        # plt.plot(dist, stagger)
        # plt.plot(dist[indices[0]], stagger[indices[0]], 'o')
        # plt.show()
        self.fit_dist = []

    def getData(self, items):
        for item in items:
            self.dist.append(item.distance_from_last_station_m)
            self.stagger.append(item.stagger)
        self.dist = np.array(self.dist)
        self.stagger = np.array(self.stagger)

    def peakMatch(self):
        # plt.figure(figsize=(12,6))
        s1 = get_peaks(self.dist, self.stagger, 40)
        s2 = get_peaks(self.adist, self.astagger, 20)
        ns2, ns1 = get_matches(s1, s2)
        ns1.append(self.dist[-1])
        ns2.append(self.dist[-1])
        # print(ns1,ns2)
        i = 1
        for d in self.dist:
            if d > ns2[i]:
                i += 1
            if d <= ns2[i]:
                p1 = (ns2[i-1], ns1[i-1])
                p2 = (ns2[i], ns1[i])
                k, b = get_fun(p1, p2)
                self.fit_dist.append(k*d+b)
            # else:
                # print(d,ns2[i])
        # plt.plot(self.fit_dist,self.stagger,color='r')
        # plt.show()
        return self.fit_dist

    def distFit(self):
        for i in range(len(self.items)):
            self.items[i].distance_from_last_station_m = self.fit_dist[i]
        return self.items


def get_peaks(dist, staggers, distance):
    indices = find_peaks(staggers, height=200, threshold=None, distance=distance,
                         prominence=None, width=None, wlen=None, rel_height=None,
                         plateau_size=None)
    return dist[indices[0]]


def get_matches(s1, s2):
    """ 匹配两个列表中的对应点"""
    ns1 = []
    ns2 = []
    ns3 = []
    for p in s1:
        n = np.abs(s2-p)
        # print(n)

        index = np.where(n == n.min())
        # if s2[index][0]<120:
        # print(index,s2[index])
        ns2.append(s2[index][0])
    for p in ns2:
        if p not in ns3:
            ns3.append(p)
    ns2 = ns3
    # for i in range(0,len(ns2)-1):
    #     if ns2[i]==ns2[i+1]:
    #         ns2.remove(ns2[i])
    #         break

    for p in ns2:
        n = np.abs(s1-p)
        # print(n)
        index = np.where(n == n.min())
        # print(index,s1[index])
        ns1.append(s1[index][0])
    ns1.insert(0, 0)
    ns2.insert(0, 0)
    # print(ns1,ns2)
    return ns1, ns2


def get_fun(p1, p2):
    """return 线性方程"""
    x1, y1 = p1
    x2, y2 = p2
    k = (y1 - y2) / (x1 - x2)
    b = y2 - k * x2
    return k, b


# dist=np.load('dist.npy')
# stagger=np.load('stagger.npy')
# xmatch(5,dist,stagger)
