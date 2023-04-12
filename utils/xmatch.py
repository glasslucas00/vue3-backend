import numpy as np
from scipy.signal import find_peaks
from  utils.Anchor import Anchor
import matplotlib.pyplot as plt

upanchor= Anchor('anchor_ul.csv')
def get_peaks(dist,staggers,distance):
    staggers = np.array(staggers)
    dist = np.array(dist)

    indices = find_peaks(staggers, height=200, threshold=None, distance=distance,
                prominence=None, width=None, wlen=None, rel_height=None,
                plateau_size=None)
    # print(indices)
    if distance!=40:
        plt.plot(dist, staggers)
        plt.plot(dist[indices[0]], staggers[indices[0]], 'o')
    print(dist[indices[0]])
    # print(np.diff(dist[indices[0]]))
    return dist[indices[0]]

def anchor_peaks(station):
    """get the anchor peaks"""
    stationInfo=upanchor.getStationInfo(station)
    dist=stationInfo['dist']
    stagger=stationInfo['stagger']
    return get_peaks(dist,stagger,20)   

def data_peaks(dist,stagger):
    """get the data peaks"""

    return get_peaks(dist,stagger,40) 


def get_matches(s1,s2):
    """ 匹配两个列表中的对应点"""
    ns1=[]
    ns2=[]
    for p in s1:
        n=np.abs(s2-p)
        # print(n)

        index=np.where(n==n.min())
        # if s2[index][0]<120:
        # print(index,s2[index])
        ns2.append(s2[index][0])
    # print(ns2)
    for i in range(0,len(ns2)-1):
        if ns2[i]==ns2[i+1]:
            ns2.remove(ns2[i])

    for p in ns2:
        n=np.abs(s1-p)
        # print(n)
        index=np.where(n==n.min())
        # print(index,s1[index])
        ns1.append(s1[index][0])
    ns1.insert(0,0)
    ns2.insert(0,0)
    print(ns1,ns2)
    return ns1,ns2

def get_fun(p1,p2):
    """return 线性方程"""
    x1,y1=p1
    x2,y2=p2
    k = (y1 - y2) / (x1 - x2)
    b = y2 - k * x2
    return k,b

def xmatch(station:int,dist:list,stagger:list):
    plt.figure(figsize=(20,10))
    ndist=[]
    s1=data_peaks(dist,stagger)
    s2=anchor_peaks(station)
    ns2,ns1=get_matches(s1,s2)
    ns1.append(dist[-1])
    ns2.append(dist[-1])
    print(ns1,ns2)
    i=1
    for d in dist:
        if d>ns2[i]:
            i+=1
        if d<=ns2[i]:
            p1=(ns2[i-1],ns1[i-1])
            p2=(ns2[i],ns1[i])
            k,b=get_fun(p1,p2)
            ndist.append(k*d+b) 
        else:
            print(d,ns2[i]) 
    print(len(ndist),len(dist))   
    plt.plot(ndist,stagger,color='r')
    plt.show()
    return ndist


# dist=np.load('dist.npy')
# stagger=np.load('stagger.npy')
# xmatch(5,dist,stagger)

