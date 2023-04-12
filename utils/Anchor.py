import pandas as pd
class Anchor(object):
    def __init__(self,csvfile:str):
        self.StationList={}
        self.read(csvfile)

    def read(self,csvfile:str):
        csvData = pd.read_csv(csvfile)
        csvData=csvData[:].values
        for row in csvData:
            if row[1] not in self.StationList.keys():
                self.StationList[row[1]]={'name':[],'dist':[],'stagger':[],'height':[]}
            self.StationList[row[1]]['name'].append(row[0])
            self.StationList[row[1]]['dist'].append(row[3])
            self.StationList[row[1]]['stagger'].append(-row[5])
            self.StationList[row[1]]['height'].append(row[4])
    
    def getStationInfo(self,station:int):
        if station in self.StationList.keys():
            return self.StationList[station]
        else:
            raise Exception("anchor表中无{}站点信息".format(station))