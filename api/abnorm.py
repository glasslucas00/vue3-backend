#!/usr/bin/python3

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models import models
from schema import schemas
import os
from decouple import config
import datetime
import time
from collections import Counter
from utils.Anchor import Anchor
ulanchor = Anchor(config('ULANCHOR'))
dlanchor = Anchor(config('DLANCHOR'))


def timer(func):
    def func_wrapper(*args, **kwargs):
        from time import time
        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_spend = time_end - time_start
        print('%s cost time: %.3f s' % (func.__name__, time_spend))
        return result
    return func_wrapper


@timer
def search(request: schemas.AbnormSearchTable, db: Session):
    sqltext = ''
    search_dict = {}

    for k, v in request:
        if v and v != 0:
            search_dict[k] = v
        print(k, v)
    page_index = search_dict.pop('pageIndex')
    page_size = search_dict.pop('pageSize')
    metro_name = 'abnorm_'+search_dict.pop('metro_name')
    if '33' in metro_name:
        file_head = '04033/'
    elif '32' in metro_name:
        file_head = '04032/'
    else:
        file_head = '010002/'
    sqltext2 = ''
    print('=========================\n', search_dict)

    import time
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')
    for k, v in search_dict.items():
        if k == 'timestamp_start':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k == 'timestamp_end':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
        elif k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+'>'+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+'<='+str(v)+' and '
        elif k == 'distance':
            if v:
                v = int(v)
                sqltext = sqltext+metro_name+'.distance_from_last_station_m'+'>' + \
                    str(v-10)+' and '+metro_name + \
                    '.distance_from_last_station_m'+'<'+str(v+10)+' and '
        elif k == 'direction':
            if len(v) > 1:
                pass
            else:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k == 'type':
            print(v)
            if len(v) == 1:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sear_dict[k]=v
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v) > 1 and len(v) < 5:
                for j in v:
                    sqltext2 = sqltext2+metro_name+'.'+k+'='+str(j)+' or '
                    # print(sqltext)
                sqltext2 = sqltext2.rstrip(' or ')
                sqltext2 += ' and '
                # print('ss',sqltext)
            else:
                pass
        elif k == 'level':
            print(v)
            if len(v) == 1:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v) == 2:
                # sear_dict[k]=v
                sqltext2 = sqltext2+metro_name+'.'+k+'=' + \
                    str(v[0])+' or '+metro_name+'.'+k+'='+str(v[1])+' and '
            else:
                pass

        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    sqltext2 = sqltext2.rstrip(' and ')
    print(sqltext)
    print('sqltext2', sqltext2, '\n')

    new_meas = type("new_meas", (models.baseAbnorm, models.Base), {
                    "__tablename__": metro_name})
    items = db.query(new_meas).filter(text(sqltext)).having(
        text(sqltext2)).order_by(new_meas.id_station_next).all()
    total = len(items)
    items = items[(page_index-1)*page_size:page_index*page_size]
    print('total:', total)

    arcing_min = 5
    arcing_max = 1300
    for item in items:
        if item.file_img:
            item.file_img=config("FILE_SERVER")+file_head+item.file_img
        if item.file_video:
            item.file_video=(config("FILE_SERVER")+file_head+item.file_video).replace('h264','mp4')
        if item.direction == 1:
            item.anchor_name, item.anchor_distance_m = ulanchor.getAnchorName(
                item.id_station_next, item.distance_from_last_station_m)
        else:
            item.anchor_name, item.anchor_distance_m = dlanchor.getAnchorName(
                item.id_station_next, item.distance_from_last_station_m)
        if item.type == 10:
            if item.value < arcing_min:
                item.value = arcing_min
            elif item.value > arcing_max:
                item.value = arcing_max+item.value % 100
    return {"code": 200, "message": "查询成功", 'data': {'total': total, 'items': items}}


@timer
def searchByAnchor(request: schemas.AbnormSearchTable, db: Session):
    sqltext2 = ''
    sqltext = ''
    search_dict = {}
    for k, v in request:
        if k == 'pageSize' or k == 'pageIndex':
            continue
        if v and v != 0:
            search_dict[k] = v
        # print(k, v)
    metro_name = 'abnorm_'+search_dict.pop('metro_name')
    # print('=========================\n', search_dict)

    import time
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    if 'id_station_pre' in search_dict.keys() and 'id_station_next' in search_dict.keys():
        station_sort=list(range(int(search_dict['id_station_pre']),int(search_dict['id_station_next'])))
    else:
        station_sort=list(range(1,33))
    search_dict.pop('timestamp')

    print('=========================\n', search_dict)
    for k, v in search_dict.items():
        if k == 'timestamp_start':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k == 'timestamp_end':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
        elif k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+'>'+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+'<='+str(v)+' and '
        elif k == 'distance':
            if v:
                sqltext = sqltext+metro_name+'.distance_from_last_station_m'+'>' + \
                    str(v-5)+' and '+metro_name + \
                    '.distance_from_last_station_m'+'<'+str(v+5)+' and '
        elif k == 'direction':
            if len(v) > 1:
                pass
            else:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k == 'type':
            # print(v)
            if len(v) == 1:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
            elif len(v) > 1 and len(v) < 5:
                for j in v:
                    sqltext2 = sqltext2+metro_name+'.'+k+'='+str(j)+' or '
                    # print(sqltext)
                sqltext2 = sqltext2.rstrip(' or ')
                sqltext2 += ' and '
            else:
                pass
        elif k == 'level':
            # print(v)
            if len(v) == 1:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
            elif len(v) == 2:
                sqltext2 = sqltext2+metro_name+'.'+k+'=' + \
                    str(v[0])+' or '+metro_name+'.'+k+'='+str(v[1])+' and '
            else:
                pass
        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    sqltext2 = sqltext2.rstrip(' and ')
    print(sqltext)
    new_meas = type("new_meas", (models.baseAbnorm, models.Base), {
                    "__tablename__": metro_name})
    items = db.query(new_meas).filter(text(sqltext)).having(
        text(sqltext2)).order_by(new_meas.distance_from_last_station_m).all()
    if not items:
        return {"code": 404, "message": "查询失败", 'data': {'total': 0, 'dict': []}}

    count = len(items)
    data_Dict = {}
    # print(search_dict.keys() )

    for i in station_sort:
        for item in items:
            if item.id_station_next==i:
                if item.direction == 1:
                    item.anchor_name, item.anchor_distance_m = ulanchor.getAnchorName(
                        item.id_station_next, item.distance_from_last_station_m)
                else:
                    item.anchor_name, item.anchor_distance_m = dlanchor.getAnchorName(
                        item.id_station_next, item.distance_from_last_station_m)
                if item.anchor_name not in data_Dict.keys():
                    data_Dict[item.anchor_name] = {1: 0, 2: 0, 3: 0, 10: 0, 11: 0, 20: 0, 21: 0, 41: 0}
                if item.type in [1, 2, 3, 10, 11, 20, 21, 41]:
                    data_Dict[item.anchor_name][item.type] += 1
    # print("data_Dict:",data_Dict)
    tableData=[]
    AnchorDict={'anchorname':[],'abnorm':{1:[],2:[],3:[],10:[],11:[],20:[],21:[],41:[]}}
    for key in data_Dict.keys():
        AnchorDict['anchorname'].append(key)
        AnchorDict['abnorm'][1].append(data_Dict[key][1])
        AnchorDict['abnorm'][2].append(data_Dict[key][2])
        AnchorDict['abnorm'][3].append(data_Dict[key][3])
        AnchorDict['abnorm'][10].append(data_Dict[key][10])
        AnchorDict['abnorm'][11].append(data_Dict[key][11])
        tableData.append({'anchor杆号':key, '导高异常':data_Dict[key][1],"拉出值异常":data_Dict[key][2],"磨耗异常":data_Dict[key][3],"燃弧异常":data_Dict[key][10],"温度异常":data_Dict[key][11]})

    return {"code": 200, "message": "查询成功", 'data': {'total': count, 'dict': AnchorDict,'table':tableData}}
   
@timer
def fireStatistics(request: schemas.AbnormSearchTable, db: Session):
    sqltext = ''
    search_dict = {}

    for k, v in request:
        if k == 'pageSize' or k == 'pageIndex':
            continue
        if v and v != 0:
            search_dict[k] = v
        # print(k, v)
    metro_name = 'abnorm_'+search_dict.pop('metro_name')
    # print('=========================\n', search_dict)
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')

    # print('=========================\n', search_dict)
    for k, v in search_dict.items():
        if k == 'timestamp_start':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k == 'timestamp_end':
            if v:
                sqltext = sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
        elif k == 'id_station_pre':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+'>'+str(v)+' and '
        elif k == 'id_station_next':
            if v:
                sqltext = sqltext+metro_name + \
                    '.id_station_next'+'<='+str(v)+' and '
        # if k=='timestamp':
        #     if v:
        #         sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '+metro_name+'.timestamp'+'<'+str(v+86400000)+' and '
        elif k == 'direction':
            if len(v) > 1:
                pass
            else:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k == 'type':
            pass

        elif k == 'level':
            print(v)
            if len(v) == 1:
                sqltext = sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
            elif len(v) == 2:
                sqltext = sqltext+metro_name+'.'+k+'=' + \
                    str(v[0])+' or '+metro_name+'.'+k+'='+str(v[1])
            else:
                pass

        elif v and v != 0:
            sqltext = sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext = sqltext.rstrip(' and ')
    # print("sqltext:", sqltext)

    new_abnorm = type("new_abnorm", (models.baseAbnorm, models.Base), {
                      "__tablename__": metro_name})
    
    items = db.query(new_abnorm.timestamp, new_abnorm.id, new_abnorm.value).filter(
        new_abnorm.type == 10).filter(text(sqltext)).order_by(new_abnorm.timestamp).all()
    print("items---len:", len(items))

    arcing_min = 5
    arcing_max = 1300
    new_list = []
    item_x = 0
    for item in items:
        item_x = item[2]
        if item[2] < arcing_min:
            item_x = arcing_min
        elif item[2] > arcing_max:
            item_x = arcing_max+item[2] % 100
        new_list.append((item[0], item[1], item_x))
    items = new_list
    if items:
        max_time = cover_time(items[0])
        plist = []
        start_timestamp = items[0][0]
        end_timestamp = 0
        i = 0
        j = 0
        for item in items:
            if item[0] > max_time:
                plist.append((max_time, i, end_timestamp-start_timestamp, j))
                max_time = cover_time(item)
                i = item[2]
                j = 1
            else:
                i = i+item[2]
                j = j+1
                end_timestamp = item[0]
        plist.append((max_time, i, end_timestamp-start_timestamp, j))
        data_dict = []
        for i in plist:
            data_dict.append(
                {'timestamp': i[0], 'value': i[1], 'runtime_day': i[2], 'count': i[3]})
        count = len(items)
        return {"code": 200, "message": "查询成功", 'data': {'total': 0, 'items': data_dict}}
    else:
        return {"code": 404, "message": "查询失败", 'data': {'total': 0, 'items': []}}


def searchXG(request: schemas.AbnormSearchTable, db: Session):
    import time

    search_dict = {}
    for k, v in request:
        if v and v != 0:
            search_dict[k] = v
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')
    page_index = search_dict.pop('pageIndex')
    page_size = search_dict.pop('pageSize')
    print(search_dict)
    metro_name = search_dict.pop('metro_name')
    if '33' in metro_name:
        file_head = '04033/'
    elif '32' in metro_name:
        file_head = '04032/'
    else:
        file_head = '010002/'

    print(metro_name)
    # search_dict.pop('type')
    FILE_PATH = config("FILE_PATH")+file_head
    items = []
    new_items = []
    date_file_list = []
    for f in os.listdir(FILE_PATH):
        if f.startswith("20"):
            days = datetime.datetime.strptime(f, "%Y-%m-%d")
            timestamp = int(days.timestamp()*1000)
            if "timestamp_start" in search_dict.keys():
                if timestamp >= search_dict['timestamp_start'] and timestamp <= search_dict['timestamp_end']:
                    date_file_list.append(f)
                else:
                    continue
    for file_name in date_file_list:
        # print(file_name)
        file_name_now = os.path.join(FILE_PATH, file_name)
        files = os.listdir(file_name_now)
        for f in files:
            if f.startswith("xg-2") and f.endswith("jpg") and len(f) > 30:
                timestamp = f[3:26]
                dt = datetime.datetime.strptime(
                    timestamp, "%Y-%m-%d_%H-%M-%S.%f")
                # print(dt.strftime('%Y-%m-%d %H:%M:%S'))
                timestamp = int(dt.timestamp()*1000)

                # a=f.index('!')
                b = f.index('(')
                c = f.index(')')
                d = f.index('[')
                e = f.index(']')
                direction = int(f[d+1:e])
                id_station_next = int(f[e+1:b])
                distance_from_last_station_m = float(f[b+1:c-2])*1000
                file_img = os.path.join(file_name+'/', f)
                items.append({'timestamp': timestamp, 'direction': direction, 'id_station_next': id_station_next, 'distance_from_last_station_m': distance_from_last_station_m,
                              'file_img': file_head+file_img})
    total = len(items)
    print('**total*', total)
    for item in items[(page_index-1)*page_size:page_index*page_size]:
        # print(search_dict)
        if "direction" in search_dict.keys():
            if item["direction"] in search_dict["direction"]:
                # items.pop(item)
                pass
            else:
                continue
        if "timestamp_start" in search_dict.keys():
            if item['timestamp'] >= search_dict['timestamp_start'] and item['timestamp'] <= search_dict['timestamp_end']:
                pass
            else:
                continue

        if "distance" in search_dict.keys():

            search_dict["distance"] = float(search_dict["distance"])
            # print(item["distance_from_last_station_m"],abs(item["distance_from_last_station_m"]-search_dict["distance"]))
            if abs(item["distance_from_last_station_m"]-search_dict["distance"]) < 10:
                pass
            else:
                continue

        if "id_station_next" in search_dict.keys():
            if item['id_station_next'] > search_dict['id_station_pre'] and item['id_station_next'] <= search_dict['id_station_next']:
                pass
            else:
                continue

        if item['direction'] == 1:
            item['anchor_name'], item['anchor_distance_m'] = ulanchor.getAnchorName(
                item['id_station_next'], item['distance_from_last_station_m'])
        else:
            item['anchor_name'], item['anchor_distance_m'] = dlanchor.getAnchorName(
                item['id_station_next'], item['distance_from_last_station_m'])
        # item['anchor_name'],item['anchor_distance_m']=canchor.getAnchorName(item['direction'],item["id_station_next"],item['distance_from_last_station_m'])
        new_items.append(item)

    print(len(new_items))
    return {"code": 200, "message": "查询成功", 'data': {'total': total, 'items': new_items}}


def delXG(request: str):
    s = request.file_img.index(':88')
    print('Delete', request.file_img)
    # print(request.file_img[s+4:])
    relatepath = request.file_img[s+4:]

    FILE_PATH = config("FILE_PATH")
    os.remove(FILE_PATH+relatepath)
    return {"code": 200, "message": "已删除", 'data': {}}


def cover_time(items):
    oneday = datetime.timedelta(days=1)
    time_max = datetime.datetime.strptime(datetime.datetime.fromtimestamp(
        items[0] / 1000).strftime("%Y-%m-%d"), "%Y-%m-%d")+oneday
    x_int = int(round(time_max.timestamp()))*1000
    # print(time_max,x_int)
    return x_int


def dual_val(val):
    if val < 5:
        return 5
    elif val > 1300:
        return 1300+val % 100
    else:
        return val


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
