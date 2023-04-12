#!/usr/bin/python3

from sqlalchemy import Column, ForeignKey, Integer, String,Float,BigInteger,Boolean
from sqlalchemy.orm import relationship
from database.configuration import Base

# train
class train_info(Base):
    # 指定本类映射到表
    __tablename__ = 'train_info'
    # 数据库中的每一列（mysql）
    id_train = Column(String(64), primary_key=True)  # 车号
    timestamp = Column(Integer)  # 最近一次车地通信
    id_station_dst = Column(Integer)  # 终点站编号
    id_station_pre = Column(Integer)  # 上一站编号
    id_station_next = Column(Integer)  # 下一站站编号
    velocity_km_per_h = Column(Float)  # 车速
    distance_from_last_station_m = Column(Float)  # 距离上一站驶出距离
    direction = Column(Integer)  # 方向
    id_tour = Column(Integer)  # 趟次
    version = Column(String)  # 车载软件版本
    info = Column(Integer)  # 预留


# meas
# class meas(Base):
#     __tablename__ = "meas_hz10_001"
#     id = Column(Integer, primary_key=True)  # 编号
#     timestamp = Column(Integer)  # 时间戳
#     id_station_dst = Column(Integer)  # 终点站
#     id_station_pre = Column(Integer)  # 上一站
#     id_station_next = Column(Integer)  # 下一站
#     velocity_km_per_h = Column(Float)  # 车速
#     distance_from_last_station_m = Column(Float)  # 距离上一站距离
#     direction = Column(Float)  # 方向
#     id_tour = Column(Integer)  # 趟次
#     is_anchor = Column(Integer)  # 是否为杆位置
#     anchor_name = Column(String)  # 杆号
#     anchor_distance_m = Column(Float)  # 距离杆位置
#     height = Column(Float)  # 导高
#     stagger = Column(Float)  # 拉出值
#     height_other = Column(Float)  # 双线时另一导高
#     stagger_other = Column(Float)  # 双线时另一拉出
#     abrasion = Column(Float)  # 磨耗
#     temperature_min = Column(Float)  # 最低温度
#     temperature_avg = Column(Float)  # 平均温度
#     temperature_max = Column(Float)  # 最高温度
#     current = Column(Float)  # 电流
#     voltage = Column(Float)  # 电压
#     force = Column(Float)  # 弓受力
#     acc = Column(Float)  # 弓加速度



# baseMeas
class baseMeas:
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)  # 编号
    timestamp = Column(Integer)  # 时间戳
    id_station_dst = Column(Integer)  # 终点站
    id_station_pre = Column(Integer)  # 上一站
    id_station_next = Column(Integer)  # 下一站
    velocity_km_per_h = Column(Float)  # 车速
    distance_from_last_station_m = Column(Float)  # 距离上一站距离
    direction = Column(Float)  # 方向
    id_tour = Column(Integer)  # 趟次
    is_anchor = Column(Integer)  # 是否为杆位置
    anchor_name = Column(String)  # 杆号
    anchor_distance_m = Column(Float)  # 距离杆位置
    height = Column(Float)  # 导高
    stagger = Column(Float)  # 拉出值
    height_other = Column(Float)  # 双线时另一导高
    stagger_other = Column(Float)  # 双线时另一拉出
    abrasion = Column(Float)  # 磨耗
    temperature_min = Column(Float)  # 最低温度
    temperature_avg = Column(Float)  # 平均温度
    temperature_max = Column(Float)  # 最高温度
    current = Column(Float)  # 电流
    voltage = Column(Float)  # 电压
    force = Column(Float)  # 弓受力
    acc = Column(Float)  # 弓加速度


# abnorm
# class abnorm(Base):
#     __tablename__ = "abnorm_hz10_001"
#     id = Column(Integer, primary_key=True)  # 编号
#     timestamp = Column(Integer)  # 时间戳
#     id_station_dst = Column(Integer)  # 终点站
#     id_station_pre = Column(Integer)  # 上一站
#     id_station_next = Column(Integer)  # 下一站
#     velocity_km_per_h = Column(Float)  # 车速
#     distance_from_last_station_m = Column(Float)  # 距离上一站距离
#     direction = Column(Float)  # 方向
#     id_tour = Column(Integer)  # 趟次
#     anchor_name = Column(String)  # 杆号
#     anchor_distance_m = Column(Float)  # 距离杆位置
#     type = Column(Integer)  # 告警类型
#     level = Column(Integer)  # 告警等级
#     value = Column(Float)  # 测量值
#     info = Column(String)  # 备注
#     file_img = Column(String)  # 告警图片路径
#     file_video = Column(String)  # 告警视频路径
#     confirm = Column(Integer)  # 告警确认


# baseAbnorm
class baseAbnorm:
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)  # 编号
    timestamp = Column(Integer)  # 时间戳
    id_station_dst = Column(Integer)  # 终点站
    id_station_pre = Column(Integer)  # 上一站
    id_station_next = Column(Integer)  # 下一站
    velocity_km_per_h = Column(Float)  # 车速
    distance_from_last_station_m = Column(Float)  # 距离上一站距离
    direction = Column(Float)  # 方向
    id_tour = Column(Integer)  # 趟次
    anchor_name = Column(String)  # 杆号
    anchor_distance_m = Column(Float)  # 距离杆位置
    type = Column(Integer)  # 告警类型
    level = Column(Integer)  # 告警等级
    value = Column(Float)  # 测量值
    info = Column(String)  # 备注
    file_img = Column(String)  # 告警图片路径
    file_video = Column(String)  # 告警视频路径
    confirm = Column(Integer)  # 告警确认


# anchor
# class anchor_table(Base):
#     __tablename__ = "anchor"
#     id = Column(Integer,primary_key=True,)
#     name = Column(String)
#     distance = Column(Float)
