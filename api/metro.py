#!/usr/bin/python3
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import models
from schema import schemas
from sqlalchemy import text, func
from decouple import config
from time import time
from utils.Anchor import Anchor
from utils.xmatch import AnchorXMatch
from utils.ymatch import AnchorYMatch
ulanchor = Anchor(config('ULANCHOR'))
dlanchor = Anchor(config('DLANCHOR'))


def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_spend = time_end - time_start
        print('%s cost time: %.3f s' % (func.__name__, time_spend))
        return result
    return func_wrapper


@timer
def search(request: schemas.MeasSearchTable, db: Session):
    """
    Get a item list
    """

    global temp_search

    sqltext = ''
    search_dict = {}

    for k, v in request:
        if v and v != 0:
            search_dict[k] = v
        print(k, v)

# 从字典提取数据
    import time
    timeArray = time.strptime(search_dict['timestamp'], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp'] = int(time.mktime(timeArray))*1000
    metro_name = 'meas_'+search_dict.pop('metro_name')
    # sort_flag = search_dict.pop('sort')
    # page = search_dict.pop('page')
    # limit = search_dict.pop('limit')
    direction = int(search_dict['direction'])
    search_dict['id_station_next'] = int(search_dict['id_station_next'])
    search_dict['id_station_pre'] = int(search_dict['id_station_pre'])
    if direction > 0:
        upanchor = ulanchor
    else:
        upanchor = dlanchor
# 如果起始站大于终点站，进行反转
    if search_dict['id_station_pre'] > search_dict['id_station_next']:
        temps = search_dict['id_station_pre']
        search_dict['id_station_pre'] = search_dict['id_station_next']
        search_dict['id_station_next'] = temps

# ******************************************1.数据库操作***********************************************************
    # 构造sql语句
    # meastypes=search_dict.pop('meastypes')
    if direction == -1:
        flag_a = '>='
        flag_b = '<'
    else:
        flag_a = '>'
        flag_b = '<='
    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_a+str(v)+' and '
        # elif k == 'meastypes':
        #     print(v)
        #     for type2 in v:
        #         range_list =search_dict[type2]
        #         sqltext = sqltext+metro_name + \
        #             '.'+type2+'>'+str(range_list[0])+' and '+metro_name + '.'+type2+'<'+str(range_list[1]) +' and '
        elif k == 'stagger' or k == 'height' or k == 'temperature_max' or k == 'abrasion' or k == 'meastypes':
            pass
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_b+str(v)+' and '
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("\nsqltext-1", sqltext)

    new_meas = type("new_meas", (models.baseMeas, models.Base),
                    {"__tablename__": metro_name})  # 构建表对象
    # items_pre = db.query(func.count('*').label('count'), new_meas.id_tour).filter(
    #     text(sqltext)).group_by(new_meas.id_tour).all()

    # ************************** 第一次搜索 **************************

    # 统计每个趟次中最大距离
    items_pre = db.query(func.max(new_meas.distance_from_last_station_m).label(
        'count'), new_meas.id_tour).filter(text(sqltext)).group_by(new_meas.id_tour).all()
    # 对距离进行排序，选择距离最短的趟次
    tour_selects = []
    for item in items_pre:
        tour_selects.append(item[0])
    if tour_selects:
        tour_selects_index = tour_selects.index(tour_selects[-2])
        search_dict['id_tour'] = str(items_pre[tour_selects_index][1])
        print('search_dict:', search_dict)
    if not tour_selects:  # 没有趟次数据，返回空
        print('Error /*日期错误')
        return {"code": status.HTTP_404_NOT_FOUND, "msg": 'Date Error', 'data': {'total': [], 'items': [], 'trueData': []}}

    if direction == -1:
        station_sort = list(range(search_dict['id_station_pre'], search_dict['id_station_next']))[
            ::-1]  # 站点数组 [2,3,4...]
    else:
        station_sort = list(
            range(search_dict['id_station_pre']+1, search_dict['id_station_next']+1))

    # ************************** 第二次搜索 **************************
    # search_dict.pop('meastypes')
    # search_dict.pop('height')
    # search_dict.pop('abrasion')
    # search_dict.pop('temperature_max')
    # search_dict.pop('meastypes')
    # 根据得到的趟次再进行搜索
    sqltext = ''
    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_a+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_b+str(v)+' and '

        elif k == 'meastypes':
            print(v)
            for type2 in v:
                range_list = search_dict[type2]
                sqltext = sqltext+metro_name + \
                    '.'+type2+'>' + \
                    str(range_list[0])+' and '+metro_name + \
                    '.'+type2+'<'+str(range_list[1]) + ' and '
        elif k == 'stagger' or k == 'height' or k == 'temperature_max' or k == 'abrasion':
            pass
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("\nsqltext-2", sqltext)

    itemsDict = {}
    for k in station_sort:
        itemsDict[k] = []
    Querys = db.query(new_meas).filter(text(sqltext)).all()
    for item in Querys:
        itemsDict[item.id_station_next].append(item)

    print('数据库总数量:', len(Querys))
    itemsList = []
    for station in station_sort:
        try:
            items = itemsDict[station]
            # sqltext2 = metro_name + '.id_station_next = '+str(station)
            # print('sqltext-3', sqltext2)
            # items=Query.filter(text(sqltext2))
            print('下一站站点 {},长度 {}'.format(station, len(items)))
            if items:
                xmatch = AnchorXMatch(station, upanchor, items)
                xmatch.peakMatch()
                items = xmatch.distFit()

                ymatch = AnchorYMatch(station, upanchor, items)
                ymatch.groupsMatch()
                items = ymatch.groupFit()
                # print('len(items)',len(items))
                for item in items:
                    itemsList.append(item)
                # print(item.stagger_other)
        except Exception as e:
            print('Error', str(e))
    count = len(itemsList)
    print('count', count)
    return {"code": 200, "message": "success", 'data': {'total': count, 'items': itemsList,  'trueData': []}}


@timer
def searchChart(request: schemas.MeasSearchTable, db: Session):
    """
    Get a item list
    """

    global temp_search

    sqltext = ''
    search_dict = {}

    for k, v in request:
        if v and v != 0:
            search_dict[k] = v
        print(k, v)

# 从字典提取数据
    import time
    timeArray = time.strptime(search_dict['timestamp'], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp'] = int(time.mktime(timeArray))*1000
    metro_name = 'meas_'+search_dict.pop('metro_name')
    # sort_flag = search_dict.pop('sort')
    # page = search_dict.pop('page')
    # limit = search_dict.pop('limit')
    direction = int(search_dict['direction'])
    search_dict['id_station_next'] = int(search_dict['id_station_next'])
    search_dict['id_station_pre'] = int(search_dict['id_station_pre'])
    if direction > 0:
        upanchor = ulanchor
    else:
        upanchor = dlanchor
# 如果起始站大于终点站，进行反转
    if search_dict['id_station_pre'] > search_dict['id_station_next']:
        temps = search_dict['id_station_pre']
        search_dict['id_station_pre'] = search_dict['id_station_next']
        search_dict['id_station_next'] = temps
    if direction == 1:
        list_distance_span_station = config('STATION', cast=lambda v: [
                                            float(s) for s in v.split(',')])
    else:
        list_distance_span_station = config('STATION_DL', cast=lambda v: [
                                            float(s) for s in v.split(',')])

# ******************************************1.数据库操作***********************************************************
    # 构造sql语句
    # meastypes=search_dict.pop('meastypes')
    if direction == -1:
        flag_a = '>='
        flag_b = '<'
    else:
        flag_a = '>'
        flag_b = '<='
    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_a+str(v)+' and '
        # elif k == 'meastypes':
        #     print(v)
        #     for type2 in v:
        #         range_list =search_dict[type2]
        #         sqltext = sqltext+metro_name + \
        #             '.'+type2+'>'+str(range_list[0])+' and '+metro_name + '.'+type2+'<'+str(range_list[1]) +' and '
        elif k == 'stagger' or k == 'height' or k == 'temperature_max' or k == 'abrasion' or k == 'meastypes':
            pass
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_b+str(v)+' and '
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("\nsqltext-1", sqltext)

    new_meas = type("new_meas", (models.baseMeas, models.Base),
                    {"__tablename__": metro_name})  # 构建表对象
    # items_pre = db.query(func.count('*').label('count'), new_meas.id_tour).filter(
    #     text(sqltext)).group_by(new_meas.id_tour).all()

    # ************************** 第一次搜索 **************************

    # 统计每个趟次中最大距离
    items_pre = db.query(func.max(new_meas.distance_from_last_station_m).label(
        'count'), new_meas.id_tour).filter(text(sqltext)).group_by(new_meas.id_tour).all()
    # 对距离进行排序，选择距离最短的趟次
    tour_selects = []
    for item in items_pre:
        tour_selects.append(item[0])
    if tour_selects:
        tour_selects_index = tour_selects.index(tour_selects[-2])
        search_dict['id_tour'] = str(items_pre[tour_selects_index][1])
        # print('\n')
        print('search_dict:', search_dict)
    if not tour_selects:  # 没有趟次数据，返回空
        return {"code": 400, "msg": "tour_selects fail", 'data': {'total': [], 'items': [], 'tour_list': [], 'trueData': []}}
    if direction == -1:
        station_sort = list(range(search_dict['id_station_pre'], search_dict['id_station_next']))[
            ::-1]  # 站点数组 [2,3,4...]
    else:
        station_sort = list(
            range(search_dict['id_station_pre']+1, search_dict['id_station_next']+1))

    # ************************** 第二次搜索 **************************
    # search_dict.pop('meastypes')
    # search_dict.pop('height')
    # search_dict.pop('abrasion')
    # search_dict.pop('temperature_max')
    # search_dict.pop('meastypes')
    # 根据得到的趟次再进行搜索
    sqltext = ''
    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_a+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_b+str(v)+' and '

        elif k == 'meastypes':
            print(v)
            for type2 in v:
                range_list = search_dict[type2]
                sqltext = sqltext+metro_name + \
                    '.'+type2+'>' + \
                    str(range_list[0])+' and '+metro_name + \
                    '.'+type2+'<'+str(range_list[1]) + ' and '
        elif k == 'stagger' or k == 'height' or k == 'temperature_max' or k == 'abrasion':
            pass
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("\nsqltext-2", sqltext)

    # Querys = db.query(new_meas).filter(text(sqltext)).all()
    
    itemsDict = {}
    for k in station_sort:
        itemsDict[k] = []
    Querys = db.query(new_meas).filter(text(sqltext)).all()
    print('Querys',len(Querys))
    for item in Querys:
        itemsDict[item.id_station_next].append(item)
    chartDatas = {'stagger':[],'height':[],'abrasion':[],'temp':[],'abrasion_other':[],'stagger_other':[],'anchorStagger':[],'anchorHeight':[],'anchorName':[]}
    for station in station_sort:
        try:
            items = itemsDict[station]
            if direction == 1:
                maxDist = sum(list_distance_span_station[0:station-1])
            else:
                maxDist = sum(list_distance_span_station[station+1:])
            xmatch = AnchorXMatch(station, upanchor, items)
            xmatch.peakMatch()
            items = xmatch.distFit()

            ymatch = AnchorYMatch(station, upanchor, items)
            ymatch.groupsMatch()
            ymatch.maxDist=maxDist
            items = ymatch.groupFit()
            for key in ymatch.chartDatas:
                for item in ymatch.chartDatas[key]:
                    chartDatas[key].append(item)
        except Exception as e:
            print('Error', str(e))
    # anchor表的数据
    return {"code": 200, "message": "success", 'data': {'chartDatas': chartDatas}}
