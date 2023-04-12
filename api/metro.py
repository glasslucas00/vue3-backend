#!/usr/bin/python3

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
# import redis   # 导入redis 模块
# import json
from models import models
from schema import schemas
from sqlalchemy import text, func
from decouple import config
import copy
import random
from time import time
from AN import anchor, canchor
from AN.mapping import MappingInfo
import AN.meas as mas


def timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_spend = time_end - time_start
        print('%s cost time: %.3f s' % (func.__name__, time_spend))
        return result
    return func_wrapper


temp_search = schemas.Meas


def get_all(metro_name: str, db: Session):
    """
    Get all meas

    Args:
        db (Session): Database session

    Returns:
        List[models.Blog]: List of blogs
    """
    new_meas = type("new_meas", (models.baseMeas, models.Base),
                    {"__tablename__": f"meas_{metro_name}"})
    return db.query(new_meas)[:100]


def create(request: schemas.Meas, db: Session):
    """
    Create a new blog

    Args:
        request (schemas.Blog): Blog object
        db (Session): Database session

    Returns:
        models.Blog: Blog object
    """
    new_metro = models.Meas(
        timestamp=request.timestamp,
        id_station_dst=request.id_station_dst,
        id_station_next=request.id_station_next,
        velocity_km_per_h=request.velocity_km_per_h,
        distance_from_last_station_m=request.distance_from_last_station_m,  # 距上一站已驶出距离
        direction=request.direction,  # 上下行方向，1上行，-1下行，0未知
        id_tour=request.id_tour,  # 趟次,
        stagger=request.stagger,  # 拉出值
        height=request.height,  # 导高
        stagger_other=request.stagger_other,  # 拉出值（预留）
        height_other=request.height_other,  # 导高（预留）
        temperature_max=request.temperature_max,  # 最高温度
        temperature_avg=request.temperature_avg,  # 平均温度
        temperature_min=request.temperature_min,  # 最低温度
        abrasion=request.abrasion,  # 磨耗
        currentc=request.currentc,  # 电流
        acc=request.acc  # 加速度
    )
    db.add(new_metro)
    db.commit()
    db.refresh(new_metro)
    return new_metro


def destroy(id: int, db: Session):
    """
    Delete a blog

    Args:
        id (int): Blog id
        db (Session): Database session

    Raises:
        HTTPException: 404 not found

    Returns:
        str: Success message
    """
    blog_to_delete = db.query(models.Meas).filter(models.Meas.timestamp == id)

    if not blog_to_delete.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {id} not found.",
        )
    blog_to_delete.delete(synchronize_session=False)
    db.commit()
    return {"done"}


def show(id: int, db: Session):
    """
    Get a blog

    Args:
        id (int): Blog id
        db (Session): Database session

    Raises:
        HTTPException: 404 not found

    Returns:
        models.Blog: Blog object
    """
    blog = db.query(models.Meas).filter(models.Meas.id == id).first()
    if blog:
        return blog
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with the id {id} is not available",
        )


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
        tour_selects_index = tour_selects.index(min(tour_selects))
        search_dict['id_tour'] = str(items_pre[tour_selects_index][1])
        print('\n')
        print('search_dict:', search_dict)
    if not tour_selects:  # 没有趟次数据，返回空
        return {"code": 1, "msg": "tour_selects fail", 'data': {'total': [], 'items': [], 'tour_list': [], 'trueData': []}}

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
                range_list =search_dict[type2]
                sqltext = sqltext+metro_name + \
                    '.'+type2+'>'+str(range_list[0])+' and '+metro_name + '.'+type2+'<'+str(range_list[1]) +' and ' 
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

    items = db.query(new_meas).filter(text(sqltext)).all()
    count = len(items)
    print('count', count)
    ss=[]
    s2=[]
    for item in items:
        ss.append(item.distance_from_last_station_m)
        s2.append(item.stagger)
    np.save('dist',np.array(ss))
    np.save('stagger',np.array(s2))
    from utils.xmatch import xmatch
    xmatch(search_dict['id_station_next'],ss,s2)
# ******************************************** 2.曲线拟合*****************************************************
    try:
        items = get_fit_item(request, search_dict, items)

    except Exception:
        return {"code": 200, "msg": "fit line fail", 'data': {'total': [], 'items': [], 'tour_list': [], 'trueData': []}}


# ****************************************** 3.杆号取值***********************************************************
    dist_dict = {}  # 距离字典 {1:[1,2,3...], 2:[1,2,3...]}
    items_dict = {}  # item字典 {1:[item1,item2...], 2:[item1,item2...]}
    if direction == -1:
        station_sort = list(range(search_dict['id_station_pre'], search_dict['id_station_next']))[
            ::-1]  # 站点数组 [2,3,4...]
    else:
        station_sort = list(
            range(search_dict['id_station_pre']+1, search_dict['id_station_next']+1))

    for item in items:
        if str(item.id_station_next) not in dist_dict.keys():
            dist_dict[str(item.id_station_next)] = []

        dist_dict[str(item.id_station_next)].append(
            item.distance_from_last_station_m)

        if str(item.id_station_next) not in items_dict.keys():
            items_dict[str(item.id_station_next)] = []

        items_dict[str(item.id_station_next)].append(item)
    # getAnchorTable 得到杆号点的测量值，拉出值拟合
    print('\n站点数组', station_sort)
    items = canchor.getAnchorTable(
        direction, dist_dict, items_dict)
    count = len(items)
    # 如果是下行，改变items的顺序

    nitems = []
    for key in station_sort:
        for item in items:
            if item.id_station_next == key:
                nitems.append(item)
    items = nitems
    tour_list = []  # 没用了
    items = canchor.remileAdd(direction, items)

    return {"code": 200, "msg": "success", 'data': {'total': count, 'items': items, 'tour_list': tour_list, 'trueData': []}}


@timer
def searchTh(request: schemas.MeasSearchDate, db: Session):
    """
    Get a item list

    Args:
        request (schemas.MeasSearchDate): Blog id
        db (Session): Database session

    Raises:
        HTTPException: 404 not found

    Returns:
        models.Blog: Blog object
    """

    global temp_search

    sqltext = ''
    search_dict = {}

    for k, v in request:
        if v and v != 0:
            search_dict[k] = v
        print(k, v)

    metro_name = 'meas_'+search_dict.pop('metro_name')
    sort_flag = search_dict.pop('sort')
    page = search_dict.pop('page')
    limit = search_dict.pop('limit')

    if 'th_list' in search_dict.keys():
        th_list = search_dict.pop('th_list')
    else:
        th_list = []

    direction = int(search_dict['direction'])
    if int(search_dict['id_station_pre']) > int(search_dict['id_station_next']):
        temps = search_dict['id_station_pre']
        search_dict['id_station_pre'] = search_dict['id_station_next']
        search_dict['id_station_next'] = temps
    flag_a = '>'
    flag_b = '<='
    if direction == 1:
        search_dict['id_station_next'] = int(search_dict['id_station_next'])
        search_dict['id_station_pre'] = int(search_dict['id_station_pre'])

    if direction == -1:
        flag_a = '>='
        flag_b = '<'
        search_dict['id_station_next'] = int(search_dict['id_station_next'])
        search_dict['id_station_pre'] = int(search_dict['id_station_pre'])

    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+flag_a+str(v)+' and '
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
    print("sqltext-1", sqltext)

    new_meas = type("new_meas", (models.baseMeas, models.Base),
                    {"__tablename__": metro_name})
    items_pre = db.query(func.count('*').label('count'), new_meas.id_tour).filter(
        text(sqltext)).group_by(new_meas.id_tour).all()
    items_pre = db.query(func.max(new_meas.distance_from_last_station_m).label(
        'count'), new_meas.id_tour).filter(text(sqltext)).group_by(new_meas.id_tour).all()
    print(items_pre)

    tour_selects = []
    for item in items_pre:
        tour_selects.append(item[0])
    if tour_selects:
        tour_selects_index = tour_selects.index(min(tour_selects))
        search_dict['id_tour'] = str(items_pre[tour_selects_index][1])
        print('\n')
        print('search_dict:', search_dict)
    if not tour_selects:
        return {"code": 1, "msg": "no data", 'data': {'total': [], 'items': [], 'tour_list': [], 'trueData': []}}
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
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("sqltext-2", sqltext)

    if sort_flag == 1 or sort_flag == 2:
        print('* Table Search by pages')
        items = db.query(new_meas).filter(text(sqltext)).all()
        count = len(items)
        print('count', count)
# ****************************************************
        items = get_fit_item(request, search_dict, items)
        # try:
        #     items=get_fit_item(request,search_dict,items)

        # except Exception:
        #     return   {"code":2,"msg":"no data",'data':{'total':[],'items': [],'tour_list':[],'trueData':[]}}

    elif sort_flag == 3:
        print('* Table Search by Th')
        sql = ''
        abnorm_type = ''
        print(th_list)
        for query in th_list:
            if query['type'] == 'info' and query['value'] > query['range'][0] and query['direction'] == 'up':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' or '
                abnorm_type = query['abnorm_type']
                continue
            elif query['type'] == 'warning' and query['value'] > query['range'][0] and query['abnorm_type'] != abnorm_type and query['direction'] == 'up':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' or '
                abnorm_type = query['abnorm_type']
                continue
            elif query['type'] == 'danger' and query['value'] > query['range'][0] and query['abnorm_type'] != abnorm_type and query['direction'] == 'up':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' or '
                continue
        for query in th_list:
            if query['type'] == 'info' and query['value'] > query['range'][0] and query['direction'] == 'down':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'<'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'<'+str(query['value'])+' or '
                abnorm_type = query['abnorm_type']
                continue
            elif query['type'] == 'warning' and query['value'] > query['range'][0] and query['abnorm_type'] != abnorm_type and query['direction'] == 'down':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'<'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'<'+str(query['value'])+' or '
                abnorm_type = query['abnorm_type']
                continue
            elif query['type'] == 'danger' and query['value'] > query['range'][0] and query['abnorm_type'] != abnorm_type and query['direction'] == 'down':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'<'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'<'+str(query['value'])+' or '
                continue
        for query in th_list:
            if query['type'] == 'info' and query['value'] > query['range'][0] and query['direction'] == 'no':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                abnorm_type = query['abnorm_type']
                continue
            elif query['type'] == 'warning' and query['value'] > query['range'][0] and query['abnorm_type'] != abnorm_type and query['direction'] == 'no':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                abnorm_type = query['abnorm_type']
                continue
            elif query['type'] == 'danger' and query['value'] > query['range'][0] and query['abnorm_type'] != abnorm_type and query['direction'] == 'no':
                if query['abnorm_type'] in sql:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                else:
                    sql = sql+metro_name+'.' + \
                        query['abnorm_type']+'>'+str(query['value'])+' and '
                continue
        sql = sql.rstrip(' and ')
        sql = sql.rstrip(' or ')
        print('sql:', sql)
        print('sqltext:', sqltext)
        items = db.query(new_meas).filter(text(sqltext)).filter(
            text(sql))[(page-1)*limit:page*limit]
        count = db.query(new_meas).filter(text(sql)).count()
        items = get_fit_item(request, search_dict, items)
        # count=len(items)
    else:
        items = []
        count = 0

    sort_anchor = {}
    sort_stagger = {}
    sort_stagger_other = {}
    items_dict = {}
    station_sort = []
    # for item in items[-10:]:
    #     print(item.distance_from_last_station_m)
    # print('len items5',len(items))
    if sort_flag == 1 or sort_flag == 2:
        for item in items:

            if item.id_station_next not in station_sort:
                station_sort.append(item.id_station_next)
            if str(item.id_station_next) not in sort_anchor.keys():
                sort_anchor[str(item.id_station_next)] = []
            sort_anchor[str(item.id_station_next)].append(
                item.distance_from_last_station_m)
            if str(item.id_station_next) not in items_dict.keys():
                items_dict[str(item.id_station_next)] = []
            items_dict[str(item.id_station_next)].append(item)
            # item.anchor_name,item.anchor_distance_m=anchor.testSearchTable(item.
            # direction,item.id_station_next,[item.distance_from_last_station_m])
        items = canchor.getAnchorTable(
            int(search_dict['direction']), sort_anchor, items_dict)
        count = len(items)
        # if sort_flag==1 :
        #     items =items[(page-1)*limit:page*limit]

    else:
        for item in items:
            item.anchor_name, item.anchor_distance_m = canchor.getAnchorName(
                item.direction, item.id_station_next, item.distance_from_last_station_m)
    # print('----',station_sort)
    if items[0].direction == -1:
        station_sort.reverse()
        # print(station_sort)
        nitems = []
        for key in station_sort:
            for item in items:
                if item.id_station_next == key:
                    nitems.append(item)

        items = nitems
    print('len items2', len(items))
    # item.anchor_name,item.anchor_distance_m=canchor.getAnchorTable(item.direction,item.id_station_next,item.distance_from_last_station_m)
    # print(item.anchor_name,item.anchor_distance_m)

    # print('items,count:',items,count)
    # id_tour_list=db.query(new_meas.id_tour.distinct().label("tours")).filter(text(sqltext)).order_by('tours')
    # print("id_tour_list",[row.tours for row in id_tour_list.all()])
    # print(count)
    # tour_list=[row.tours for row in id_tour_list.all()]
    tour_list = []
    temp_search = request
    # if search_dict['direction']==-1:
    #     items=items.reverse()
    items = canchor.remileAdd(direction, items)
    return {"code": 0, "msg": "success", 'data': {'total': count, 'items': items, 'tour_list': tour_list, 'trueData': []}}

temp_data = []

@timer
# 测量数据曲线
def searchChart(request: schemas.MeasSearchTable, db: Session):
    """

    """
    sqltext = ''
    search_dict = {}
    for k, v in request:
        if v and v != 0:
            search_dict[k] = v
    metro_name = 'meas_'+search_dict.pop('metro_name')
    # sort_flag = search_dict.pop('sort')
    # page = search_dict.pop('page')
    # limit = search_dict.pop('limit')
    print('search_dict:', search_dict)
    direction = int(search_dict['direction'])
    import time
    timeArray = time.strptime(search_dict['timestamp'], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp'] = int(time.mktime(timeArray))*1000

    if int(search_dict['id_station_pre']) > int(search_dict['id_station_next']):
        temps = search_dict['id_station_pre']
        search_dict['id_station_pre'] = search_dict['id_station_next']
        search_dict['id_station_next'] = temps
    if direction == 1:
        search_dict['id_station_next'] = int(search_dict['id_station_next'])
        search_dict['id_station_pre'] = int(search_dict['id_station_pre'])
        mark_a = '>'
        mark_b = '<='
    if direction == -1:
        search_dict['id_station_next'] = int(search_dict['id_station_next'])
        search_dict['id_station_pre'] = int(search_dict['id_station_pre'])
        mark_a = '>='
        mark_b = '<'
    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+mark_a+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+mark_b+str(v)+' and '
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("sqltext:", sqltext)

    new_meas = type("new_meas", (models.baseMeas, models.Base),
                    {"__tablename__": metro_name})
    items_pre = db.query(func.count('*').label('count'), new_meas.id_tour).filter(
        text(sqltext)).group_by(new_meas.id_tour).all()
    items_pre = db.query(func.max(new_meas.distance_from_last_station_m).label(
        'count'), new_meas.id_tour).filter(text(sqltext)).group_by(new_meas.id_tour).all()
    print(items_pre)
    tour_selects = []
    for item in items_pre:
        tour_selects.append(item[0])
    if tour_selects:
        tour_selects_index = tour_selects.index(min(tour_selects))
        search_dict['id_tour'] = str(items_pre[tour_selects_index][1])
        print('\n')
        print('search_dict:', search_dict)

    sqltext = ''
    for k, v in search_dict.items():
        if k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+mark_a+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+mark_b+str(v)+' and '
        elif k == 'timestamp':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>' + \
                    str(v)+' and '+metro_name+'.timestamp' + \
                    '<'+str(v+86400000)+' and '
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    print("sqltext-2:", sqltext)

    #  temp_data = db.query(new_meas.id_station_next,new_meas.distance_from_last_station_m,new_meas.height
    #     ,new_meas.stagger,new_meas.height_other,new_meas.stagger_other,new_meas.abrasion,new_meas.temperature_avg).filter(text(sqltext))
    items = db.query(new_meas).filter(text(sqltext)).order_by(
        new_meas.id_station_next).order_by(new_meas.distance_from_last_station_m).all()
    ################################  以上  数据库查询      #################################

    # 数据拟合
    itemslist = get_fit_item(request, search_dict, items)

    if int(search_dict['direction']) == 1:
        list_distance_span_station = config('STATION', cast=lambda v: [
                                            float(s) for s in v.split(',')])
    else:
        list_distance_span_station = config('STATION_DL', cast=lambda v: [
                                            float(s) for s in v.split(',')])

    if direction == -1:
        station_sort = list(range(search_dict['id_station_pre'], search_dict['id_station_next']))[
            ::-1]  # 站点数组 [2,3,4...]
    else:
        station_sort = list(
            range(search_dict['id_station_pre']+1, search_dict['id_station_next']+1))

    trueMeasData = canchor.getTrueData(
        int(search_dict['direction']), station_sort)  # anchor表的数据
    # new_set = canchor.getAnchor(direction, station_sort)
    new_set = []  # 没用了
    for item in items:
        item.anchor_name, item.anchor_distance_m = canchor.getAnchorName(
            item.direction, item.id_station_next, item.distance_from_last_station_m)
        item.abrasion_other, item.abrasion = canchor.refineAbrasion(
            item.anchor_name, item.abrasion)
    # for item in itemslist:
        # items=canchor.getAnchorTable(int(search_dict['direction']),sort_anchor,items_dict)
    # id_tour_list=db.query(new_meas.id_tour.distinct().label("tours")).order_by('tours')
    # tour_list=[row.tours for row in id_tour_list.all()]
    return {"code": 200, "msg": "success", 'data': {'total': new_set, 'items': itemslist, 'tour_list': list_distance_span_station, 'trueData': trueMeasData}}


def get_fit_item(request, search_dict, items):
    direction = int(search_dict['direction'])
    if direction == -1:
        station_sort = list(range(search_dict['id_station_pre'], search_dict['id_station_next']))[
            ::-1]  # 站点数组 [2,3,4...]
    else:
        station_sort = list(
            range(search_dict['id_station_pre']+1, search_dict['id_station_next']+1))
    if direction == 1:
        list_distance_span_station = config('STATION', cast=lambda v: [
                                            float(s) for s in v.split(',')])
    else:
        list_distance_span_station = config('STATION_DL', cast=lambda v: [
                                            float(s) for s in v.split(',')])

    itemslist = []
    data_dict = dict()
    #############################   去单个双线    ###################################
    # 如果拉出值2只有一个单值，去除其
    for i in range(1, len(items)-1):
        if items[i].stagger_other:
            if items[i-1].stagger_other == None and items[i+1].stagger_other == None:
                items[i].stagger_other = None

    #############################  距离筛选 ###################################
    for item in items[:]:
        if direction == 1:
            maxdistance = list_distance_span_station[item.id_station_next-1]
        else:
            maxdistance = list_distance_span_station[item.id_station_next]
        # print(item.id_station_next,maxdistance,item.distance_from_last_station_m)

        # 杭10下行11号站点数据有偏差，做下处理
        if item.id_station_next == 11 and direction == -1:
            if item.distance_from_last_station_m > 285.5:
                item.distance_from_last_station_m -= 285.5
                # itemslist.append(item)
            else:
                item.distance_from_last_station_m += 10000
        if item.distance_from_last_station_m < maxdistance:
            itemslist.append(item)
            if item.id_station_next not in data_dict.keys():
                data_dict[item.id_station_next] = [[], [], []]
            data_dict[item.id_station_next][0].append(
                item.distance_from_last_station_m)
            data_dict[item.id_station_next][1].append(item.stagger)
            data_dict[item.id_station_next][2].append(item.stagger_other)

    item_doubleline_dict = {}
    for key in data_dict.keys():
        item_doubleline_dict[key] = mas.getKeyPointsPlus(
            data_dict[key][0], data_dict[key][1], data_dict[key][2], 12)
    print("item_doubleline_dict", item_doubleline_dict)  # 测量数据双线字典
    anchor_doubleline_dict = searchDoubleAnchors(request)
    print('anchor_doubleline_dict', anchor_doubleline_dict)  # anchor表双线字典

    # ******************************* x轴缩放 *********************************
    #item_doubleline_dict，anchor_doubleline_dict加上站点最后的距离
    for key in station_sort:
        if direction == 1:
            # print('===key====', key,list_distance_span_station[key-1], 'inverse_flag', inverse_flag)
            item_doubleline_dict[key].append(list_distance_span_station[key-1])
            anchor_doubleline_dict[key].append(
                list_distance_span_station[key-1])
        else:
            # print('===key====', key,list_distance_span_station[key], 'inverse_flag', inverse_flag)
            item_doubleline_dict[key].append(list_distance_span_station[key])
            anchor_doubleline_dict[key].append(list_distance_span_station[key])
        # item_doubleline_dict，anchor_doubleline_dict的每个区间进行匹配
        item_doubleline_dict[key], anchor_doubleline_dict[key] = remaping(
            item_doubleline_dict[key], anchor_doubleline_dict[key], direction)
        
        x_m = MappingInfo()
        range_stagger_dict = {}
        range_distance_dict = {}
        for item in itemslist:
            if item.id_station_next == int(key):
                maping_instance = findOrderIndex(
                    item_doubleline_dict[key], anchor_doubleline_dict[key], item.distance_from_last_station_m)
                # print('origin',item.distance_from_last_station_m)
                x_m.getMappingInfo(
                    maping_instance[0], maping_instance[1], maping_instance[2], maping_instance[3])
                dict_index = maping_instance[0]+maping_instance[1]
                if dict_index not in range_stagger_dict.keys():
                    range_stagger_dict[dict_index] = []
                if dict_index not in range_distance_dict.keys():
                    range_distance_dict[dict_index] = []
                range_stagger_dict[dict_index].append(item.stagger)
                range_distance_dict[dict_index].append(
                    item.distance_from_last_station_m)
                item.distance_from_last_station_m = x_m.transMeasToAnchor(
                    item.distance_from_last_station_m)

    # ******************************* 补双线 *********************************
    sort_items = []
    for key in station_sort:
        tempa = []
        for item in itemslist:
            if item.id_station_next == int(key):
                tempa.append(item)
        tempb = addPoint(tempa)
        sort_items.extend(tempb)
    itemslist = sort_items
    # ******************************* 补双线 *********************************
    ##################  转成全线距离    ##################
    itemslist = canchor.mileAdd(direction, itemslist)

    # 划分区间
    stagger_groups = []
    item_groups = []
    data_a = []
    data_b = []
    a = []
    b = []
    ######################将item、stagger 数据按双线区间进行划分##########################
    for x in itemslist:
        if x.stagger_other:
            if a[-1]*x.stagger_other > 0:
                data_a.append(x)
                data_b.append(x)
                b.append(x.stagger)
                a.append(x.stagger_other)
            else:
                data_a.append(x)
                data_b.append(x)
                a.append(x.stagger)
                b.append(x.stagger_other)
            # tempstagger.append(x.stagger_other)
        else:
            if len(b) > 1:
                stagger_groups.append(a)
                item_groups.append(data_a)
                a = b
                data_a = data_b
                b = []
                data_b = []
                a.append(x.stagger)
                data_a.append(x)
            else:
                a.append(x.stagger)
                data_a.append(x)
    stagger_groups.append(a)  #[[group1],[group2]]
    item_groups.append(data_a)#[[item_groups],[item_groups]]
    # 按双线区间找到杆号区间，对拉出值进行拟合
    for i in range(len(item_groups)):
        item_group = item_groups[i]
        stagger_group = stagger_groups[i]
        item = item_group[int(len(item_group)/2)]

        stagger_groups[i] = canchor.getAnchorStagger_bygroup(
             item.id_station_next, item_group, stagger_group, item)
    data_a = []
    data_b = []

    #将分组进行恢复
    for item in itemslist:
        # print('\n','hhhh')
        if len(stagger_groups[0]) == 0:
            stagger_groups.pop(0)
        if item.stagger_other:
            item.stagger = stagger_groups[0].pop(0)
            item.stagger_other = stagger_groups[1].pop(0)
        else:
            item.stagger = stagger_groups[0].pop(0)
    return itemslist


def addPoint(itemslist):
    list_dist = []
    list_stagger = []
    list_stagger_other = []

    for item in itemslist:
        list_dist.append(item.distance_from_last_station_m)
        list_stagger.append(item.stagger)
        list_stagger_other.append(item.stagger_other)

    for i in range(len(list_stagger)-5):
        random.seed(int(list_stagger[i]))
        if abs(list_stagger[i]-list_stagger[i+1]) > 225 and list_stagger_other[i+1] == None \
                and list_stagger_other[i] == None and abs(list_dist[i]-list_dist[i+1]) > 0.2:
            print('===list_dist====', list_dist[i])
            for j in range(i+1, i+5):
                if list_stagger[j] > 0:
                    itemslist[j].stagger_other = itemslist[j].stagger - \
                        random.uniform(270, 285)
                else:
                    itemslist[j].stagger_other = itemslist[j].stagger + \
                        random.uniform(270, 285)

    list_stagger = []
    list_stagger_other = []
    for item in itemslist:
        list_stagger.append(item.stagger)
        list_stagger_other.append(item.stagger_other)
    for i in range(len(list_stagger)-5):
        a = list_stagger[i]
        b = list_stagger[i+1]
        c = list_stagger[i+2]
        ao = list_stagger_other[i]
        bo = list_stagger_other[i+1]
        co = list_stagger_other[i+2]

        if abs(a-b) > 180 and abs(a-c) < 120 and ao == None and bo == None and co == None:
            itemslist[i+1].stagger = (a+c)/2

    return itemslist


def remaping(data_list: list, anchor_doubleline_dict: list, flag):
    # print('---------------',data_list,anchor_doubleline_dict,insert_data)
    # new=[]
    # new2=[]
    if flag > 0:
        vals = 35
    else:
        vals = 50
    end = anchor_doubleline_dict[-1]
    print('end', end)
    anchor_doubleline_dict = anchor_doubleline_dict[:-1]
    data_list = copy.deepcopy(data_list[:-1])
    res_list = []
    num = min(len(anchor_doubleline_dict), len(data_list))
    for i in range(len(anchor_doubleline_dict)):
        a = anchor_doubleline_dict[i]
        for j in range(len(data_list)):
            b = data_list[j]
            if abs(a-b) < vals:
                res_list.append((a, b))
                data_list.remove(b)
                break
            else:
                continue
    res_list.append((end, end))
    print('res_list', res_list)
    n1 = []
    n2 = []
    for item in res_list:
        n1.append(item[0])
        n2.append(item[1])
    return n1, n2


def findOrderIndex(n1: list, n2: list, insert_data: float):
    """为n2中每一个元素找到其在n1中最近的点的索引位置"""
    num = len(n2)
    for i in range(num):
        if insert_data <= n2[i]:
            # print('ii',i)
            if i == 0:
                # print(i,[0,n2[i],0,anchor_doubleline_dict[i]])
                return [0, n2[i], 0, n1[i]]
            else:
                # print(i ,[n2[i-1],n2[i],n1[i-1],n1[i]])
                return [n2[i-1], n2[i], n1[i-1], n1[i]]
        elif insert_data > n2[num-1]:
            # print(insert_data,n2,n1,n2[num-1])
            return None

        else:
            continue


# searchAnchors
def searchDoubleAnchors(request: schemas.MeasSearchDate):
    """ 
    检测双线的位置
    返回字典
    {
        8: [37.4, 221.79, 338.19, 574.59, 810.99, 1047.39, 1283.79], 
        7: [74.4, 94.8, 320.95, 557.35, 793.75, 1030.15, 1050.55], 
        6: [36.21, 188.61, 351.68, 564.68, 671.24, 823.64, 892.04], 
    anchor    5: [35.9, 222.06, 338.46, 574.86, 811.26, 1047.66],   =>[35.9,..]
    itemdata    5: [12 ,36.9, 103, 338.46, 574.86, 811.26, 1047.66],  =>[36.9,..]
        ......
    }
    """
    if temp_search:
        pass
    search_dict = {}
    for k, v in request:
        search_dict[k] = v
    if int(search_dict['id_station_pre']) > int(search_dict['id_station_next']):
        temps = search_dict['id_station_pre']
        search_dict['id_station_pre'] = search_dict['id_station_next']
        search_dict['id_station_next'] = temps
    if search_dict['id_station_pre']:
        if not search_dict['id_station_next']:
            search_dict['id_station_next'] = 11
    else:
        search_dict['id_station_pre'] = 0
        if not search_dict['id_station_next']:
            search_dict['id_station_next'] = 12
    if not search_dict['direction']:
        search_dict['direction'] = 1
    # print('==',search_dict['direction'],search_dict['id_station_pre'],search_dict['id_station_next'])
    new_set, anchor_doubleline_dict = anchor.testSearchPlot(search_dict['direction'], [
        search_dict['id_station_pre'], search_dict['id_station_next']])
    # print(anchor_name,anchor_distance_m)
    return anchor_doubleline_dict

