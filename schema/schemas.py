#!/usr/bin/python3

from typing import Union, Optional,List

from pydantic import BaseModel
#列车查询


class Meas(BaseModel):
    timestamp: int=None
    id_station_dst: int=None#终点站编号
    id_station_next: int=None#下一站编号
    velocity_km_per_h: float=None#车速
    distance_from_last_station_m: float=None#距上一站已驶出距离
    direction: int=None#上下行方向，1上行，-1下行，0未知
    id_tour: int=None#趟次
    stagger : float=None#拉出值
    height : float=None#导高
    stagger_other : float=None#拉出值（预留）
    height_other : float=None#导高（预留）
    temperature_max : float=None#最高温度
    temperature_avg : float=None#平均温度
    temperature_min : float=None#最低温度
    abrasion : float=None#磨耗
    currentc : float=None#电流
    acc : float=None#加速度
    class Config:
        orm_mode = True
class MeasSearchDate(BaseModel):
    metro_name: str
    timestamp: int=None
    id_station_next: Union[str, int]=None#终点站编号
    id_station_pre: Union[str, int]=None#下一站编号
    direction: Union[str, int]=None#上下行方向，1上行，-1下行，0未知
    id_tour: Union[str, int]=None#趟次
    limit: int=None
    page:int=None
    sort:int=None
    th_list:List=None# 等级阈值
    class Config:
        orm_mode = True
class MeasSearchTable(BaseModel):
    metro_name: str
    timestamp:Union[str, int]=None
    id_station_next: Union[str, int]=None#终点站编号
    id_station_pre: Union[str, int]=None#下一站编号
    direction: Union[str, int]=None#上下行方向，1上行，-1下行，0未知
    meastypes:List=None
    stagger : List=None#拉出值
    height : List=None#导高
    temperature_max : List=None#最高温度
    abrasion : List=None#磨耗
    # id_tour: Union[str, int]=None#趟次
    # limit: int=None
    # page:int=None
    # sort:int=None
    # th_list:List=None# 等级阈值
    class Config:
        orm_mode = True
class Abnorm(BaseModel):
    id : int=None
    timestamp: int=None
    id_station_dst : int=None
    id_station_next : int=None
    velocity_km_per_h : float=None
    distance_from_last_station_m : float=None
    direction : int=None
    id_tour : int=None
    type : int=None# 告警类型
    level : int=None# 等级
    info: str=None# 备注信息
    file_img: str=None# 图像相对路径
    file_video : str=None# 视频相对路径
    confirm : int=None#是否确认为故障，此字段可忽略
    class Config:
        orm_mode = True
class AbnormSearchDate(BaseModel):
    limit: int=None
    page:int=None
    metro_name: str
    timestamp_start: int=None
    timestamp_end: int=None
    id_station_next : int=None
    id_station_pre : int=None
    direction : List=None
    type : List=None# 告警类型
    level : List=None# 等级
    distance: Union[str, int]=None
    class Config:
        orm_mode = True
class AbnormSearchTable(BaseModel):
    pageIndex: int=None
    pageSize:int=None
    metro_name: str
    timestamp: List=None
    id_station_next : int=None
    id_station_pre : int=None
    direction : List=None
    type : List=None# 告警类型
    level : List=None# 等级
    distance:Union[str, int]=None
    class Config:
        orm_mode = True
class AbnormXG(BaseModel):
    file_img: str
class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


