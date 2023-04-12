# import numpy as np
'''
# map data from [meas_s, meas_e] ---> [anchor_s, anchor_e]
usage:
    meas * ratio + offset ===> anchor
'''
class MappingInfo(object):
    def __init__(self) -> None:
        self.offset_meas_to_anchor = 0
        self.ratio_meas_to_anchor = 1.0
        self.meas_s = 0
        self.meas_e = 0
    
    def getMappingInfo(self, meas_s, meas_e, anchor_s, anchor_e):
        len_meas = meas_e - meas_s
        len_anchor = anchor_e - anchor_s
        self.ratio_meas_to_anchor = len_anchor / len_meas
        self.offset_meas_to_anchor = anchor_s - meas_s
        self.meas_s = meas_s
        self.meas_e = meas_e
        self.anchor_s = anchor_s
    def transMeasToAnchor(self, meas_val):
        if meas_val < self.meas_s or meas_val > self.meas_e:
            return None
        return (meas_val-self.meas_s)*self.ratio_meas_to_anchor + self.anchor_s

if __name__ == '__main__':
    m = MappingInfo()
    m.getMappingInfo(5, 9, 1, 100)
    # l_s = [0.1, 0.2, 0.3, 0.99]
    l_s = [6,7,8,8.9]
    l_e = list()
    for item in l_s:
        l_e.append(m.transMeasToAnchor(item))
    print(l_s)
    print(l_e)