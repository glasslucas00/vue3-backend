import numpy as np
from scipy.signal import find_peaks
# from  utils.Anchor import Anchor
from  Anchor import Anchor
import matplotlib.pyplot as plt

upanchor= Anchor('anchor_ul.csv')

def dataList(station):
    dist=np.load('dist.npy')
    stagger=np.load('stagger.npy')
    anchors_dis = dist
    anchors_stagger = stagger
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
    plt.figure(figsize=(18, 10))
    for j in range(len(stagger_a)):
        plt.plot(dis_a[j],stagger_a[j], '-x')
        # plt.plot(dis_group,stagger_group, '-o')
        plt.xlabel('Time')
        plt.ylabel('Value')
        # plt.grid()网格线设置
        plt.grid(True)
        # plt.draw()
        # plt.savefig('all.jpg')
    # plt.show()
def AnchorList(station):
    stationInfo=upanchor.getStationInfo(station)
    dist=stationInfo['dist']
    stagger=stationInfo['stagger']
    anchors_dis = dist
    anchors_stagger = stagger
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
    plt.figure(figsize=(18, 10))
    for j in range(len(stagger_a)):
        plt.plot(dis_a[j],stagger_a[j], '-x')
        # plt.plot(dis_group,stagger_group, '-o')
        plt.xlabel('Time')
        plt.ylabel('Value')
        # plt.grid()网格线设置
        plt.grid(True)
        # plt.draw()
        # plt.savefig('all.jpg')
    plt.show()
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
    # # plt.savefig('stagger_a='+str(flag)+'.jpg')
    # plt.cla()
    return dis_a, stagger_a
dataList(5)
up_dis_a, up_stagger_a = AnchorList(5)
# down_dis_a, down_stagger_a = AnchorList(-1)
