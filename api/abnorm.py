#!/usr/bin/python3

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text,func
from models import models
from schema import schemas
import os
from decouple import config
from database.configuration import Base
import datetime,time
import numpy as np
# from anchor import anchor
from AN import canchor
from collections import Counter



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
    sqltext=''
    search_dict={}
    
    for k,v in request:
        if v and v!=0:
            search_dict[k]=v             
        print(k,v)
    page_index=search_dict.pop('pageIndex')
    page_size=search_dict.pop('pageSize')
    metro_name='abnorm_'+search_dict.pop('metro_name')
    sqltext2=''
    print('=========================\n',search_dict)


    import time
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')
    for k,v in search_dict.items():
        if k=='timestamp_start':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k=='timestamp_end':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
        elif k=='id_station_pre':
            if v:
                sqltext=sqltext+metro_name+'.id_station_next'+'>'+str(v)+' and '
        elif k=='id_station_next':
            if v:
                sqltext=sqltext+metro_name+'.id_station_next'+'<='+str(v)+' and '
        elif k=='distance':
            if v:
                sqltext=sqltext+metro_name+'.distance_from_last_station_m'+'>'+str(v-5)+' and '+metro_name+'.distance_from_last_station_m'+'<'+str(v+5)+' and '
        elif k=='direction':
            if len(v)>1:
                pass
            else:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k=='type':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sear_dict[k]=v
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)>1 and len(v)<5:
                for j in v:
                    sqltext2=sqltext2+metro_name+'.'+k+'='+str(j)+' or '
                    # print(sqltext)
                sqltext2=sqltext2.rstrip(' or ')
                sqltext2+=' and '
                # print('ss',sqltext)
            else:
                pass              
        elif k=='level':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)==2:
                # sear_dict[k]=v
                sqltext2=sqltext2+metro_name+'.'+k+'='+str(v[0])+' or '+metro_name+'.'+k+'='+str(v[1])+' and '
            else:
                pass
              
        elif v and v!=0 :
            sqltext=sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext=sqltext.rstrip(' and ')
    sqltext2=sqltext2.rstrip(' and ')
    print(sqltext)
    print('sqltext2',sqltext2,'\n')
    
    new_meas = type("new_meas", (models.baseAbnorm, models.Base), {"__tablename__":metro_name})
    items = db.query(new_meas).filter(text(sqltext)).having(text(sqltext2)).order_by(new_meas.id_station_next).all()
    count = len(items) 
   

    items=items[(page_index-1)*page_size:page_index*page_size]
  
    print('count',count)
       
    arcing_min=5
    arcing_max=1300
    for item in items:
        item.anchor_name,item.anchor_distance_m=canchor.getAnchorName(item.direction,item.id_station_next,item.distance_from_last_station_m)
        # anchor.testSearchTable(item.direction,item.id_station_next,[item.distance_from_last_station_m])
        # print(item)
        if  item.type==10:
            if item.value<arcing_min:
                item.value=arcing_min
            elif item.value>arcing_max:
                item.value=arcing_max+item.value%100
    print("Item count",count)
    return {"code":200,"message":"success",'data':{'total':count,'items': items}}
@timer
def searchSort(request: schemas.AbnormSearchDate, db: Session):
    sqltext=''
    sqltext2=''
    search_dict={}
    for k,v in request:
        if v and v!=0:
            search_dict[k]=v             
        print(k,v)
    
    metro_name='abnorm_'+search_dict.pop('metro_name')
    print('search_dict:',search_dict)
    for k,v in search_dict.items():
        if k=='timestamp_start':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k=='timestamp_end':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
                
        # if k=='timestamp':
        #     if v:
        #         sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '+metro_name+'.timestamp'+'<'+str(v+86400000)+' and '
        elif k=='direction':
            if len(v)>1:
                pass
            else:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k=='type':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sear_dict[k]=v
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)>1 and len(v)<5:
                for j in v:
                    sqltext2=sqltext2+metro_name+'.'+k+'='+j+' or '
                    # print(sqltext)
                sqltext2=sqltext2.rstrip(' or ')
                sqltext2+=' and '
                # print('ss',sqltext)
            else:
                pass              
        elif k=='level':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)==2:
                # sear_dict[k]=v
                sqltext2=sqltext2+metro_name+'.'+k+'='+v[0]+' or '+metro_name+'.'+k+'='+v[1]+' and '
            else:
                pass
                    
        elif v and v!=0 :
            sqltext=sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext=sqltext.rstrip(' and ')
    sqltext2=sqltext2.rstrip(' and ')
    print("sqltext:",sqltext)
    new_abnorm = type("new_abnorm", (models.baseAbnorm, models.Base), {"__tablename__":metro_name})
    items2 = db.query(
            new_abnorm.id_tour.label('id_tour'),
            new_abnorm.direction.label('direction'),
            new_abnorm.level,
            new_abnorm.timestamp,
            func.sum(new_abnorm.value).label('value'),
            func.max(new_abnorm.timestamp).label('timestamp_max'),
            func.min(new_abnorm.timestamp).label('timestamp_min'),
        ).filter(text(sqltext)).group_by(
            'id_tour','direction').order_by(new_abnorm.timestamp).order_by(new_abnorm.id_tour).all()
    id_tour_list=[]
    items = db.query(
            new_abnorm.id_tour,
            new_abnorm.direction,
            new_abnorm.timestamp,
            new_abnorm.value
            # func.sum(new_abnorm.value).label('value'),
            # func.max(new_abnorm.timestamp).label('timestamp_max'),
            # func.min(new_abnorm.timestamp).label('timestamp_min'),
        ).filter(text(sqltext)).having(text(sqltext2)).order_by(new_abnorm.timestamp).order_by(new_abnorm.id_tour).all()

    k=0
    total_val=0
    data_list=[]
    time_sort=[]
    for item in items:
        id_tour_list.append(item[0])
       
    id_tour_list=np.array(id_tour_list)
    id_tour_list=np.unique(id_tour_list)
    for id_tour in id_tour_list:
        for item in items:
            if item[0]==id_tour:
                direction=item[1]
                timestamp=item[2]
                time_sort.append(item[2])
                total_val+=dual_val(item[3])
        time_sort=np.array(time_sort)
        # print('time_sort:: ',time_sort)
        data_list.append({'id_tour':id_tour ,'value':total_val,'timestamp_max':np.max(time_sort),'timestamp_min':np.min(time_sort),'direction':direction,'timestamp':timestamp})
        time_sort=[]
    # print(data_list)

#//////////////

  

    # for item in items:
    #     print(item[0],item[5],time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item[5]/1000)),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item[6]/1000)))
    # items2 = db.query(new_abnorm.timestamp).filter(text(sqltext)).order_by(new_abnorm.timestamp).all() 
    # count = db.query(new_abnorm).filter(text(sqltext)).count()  
    # items=items.all()
    # count=items.count()
    # items=db.query(new_abnorm.timestamp.cast( Datetime).label('t'),func.count('*').label('type_count'),new_abnorm.timestamp).filter(text(sqltext)).group_by('t').all()
    # items=db.query(func.count(new_abnorm.type).label('type_count'),func.year(new_abnorm.timestamp).label('y'),func.month(new_abnorm.timestamp).label('m'),func.day(new_abnorm.timestamp).label('d')).group_by('y','m','d').all()
    count=len(items)
    print("blog",count)
    return {"code":0,"msg":"success",'data':{'total':count,'items': items}}
@timer
# ByAnchor
def searchByAnchor(request: schemas.AbnormSearchTable, db: Session):
    sqltext2=''
    sqltext=''
    search_dict={}
    
    for k,v in request:
        if v and v!=0:
            search_dict[k]=v             
        print(k,v)
    metro_name='abnorm_'+search_dict.pop('metro_name')
    sqltext2=''
    print('=========================\n',search_dict)


    import time
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')

    print('=========================\n',search_dict)
    for k,v in search_dict.items():
        if k=='timestamp_start':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k=='timestamp_end':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
        elif k=='id_station_pre':
            if v:
                sqltext=sqltext+metro_name+'.id_station_next'+'>'+str(v)+' and '
        elif k=='id_station_next':
            if v:
                sqltext=sqltext+metro_name+'.id_station_next'+'<='+str(v)+' and '
        elif k=='distance':
            if v:
                sqltext=sqltext+metro_name+'.distance_from_last_station_m'+'>'+str(v-5)+' and '+metro_name+'.distance_from_last_station_m'+'<'+str(v+5)+' and '
        elif k=='direction':
            if len(v)>1:
                pass
            else:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k=='type':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sear_dict[k]=v
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)>1 and len(v)<5:
                for j in v:
                    sqltext2=sqltext2+metro_name+'.'+k+'='+str(j)+' or '
                    # print(sqltext)
                sqltext2=sqltext2.rstrip(' or ')
                sqltext2+=' and '
                # print('ss',sqltext)
            else:
                pass              
        elif k=='level':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)==2:
                # sear_dict[k]=v
                sqltext2=sqltext2+metro_name+'.'+k+'='+str(v[0])+' or '+metro_name+'.'+k+'='+str(v[1])+' and '
            else:
                pass
              
        # elif k=='type' or k=='level' or k=='direction':
        #     print(v)
        #     if len(v)>1:
        #         sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
        #     else:
        #         sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif v and v!=0 :
            sqltext=sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext=sqltext.rstrip(' and ')
    sqltext2=sqltext2.rstrip(' and ')
    print(sqltext)
    new_meas = type("new_meas", (models.baseAbnorm, models.Base), {"__tablename__":metro_name})
    items = db.query(new_meas).filter(text(sqltext)).having(text(sqltext2)).order_by(new_meas.id_station_next).all() 
    count = len(items) 
    data_Dict={}

    for item in items:
        # print(item.direction,item.id_station_next,[item.distance_from_last_station_m])
        item.anchor_name,item.anchor_distance_m=canchor.getAnchorName(item.direction,item.id_station_next,item.distance_from_last_station_m)
        # print(item.anchor_name)
    for item in items:
        if item.anchor_name not in data_Dict.keys():
            data_Dict[item.anchor_name]={1:0,2:0,3:0,10:0,11:0,20:0,21:0,41:0}
        if item.type in [1,2,3,10,11,20,21,41]:
            data_Dict[item.anchor_name][item.type]+=1
            
    # print(data_Dict)

    count_data=[]
    type_colletion=[]
    anchor_now_name=''
    if count:
        if  items[0].anchor_name:
            anchor_now_name=items[0].anchor_name
        for item in items:
            if item.anchor_name:
                # print('am',item.anchor_name)
                if item.anchor_name==anchor_now_name:
                    type_colletion.append(item.type)
                else:
                    if anchor_now_name:
                        count_data.append({'name':anchor_now_name,'data':dict(Counter(type_colletion))})   
                    anchor_now_name=item.anchor_name
                    type_colletion=[item.type]
        if anchor_now_name:
            count_data.append({'name':anchor_now_name,'data':dict(Counter(type_colletion))})      
            
    # print(count_data)
    anchor_list=[]
    count_dict={1:[],2:[],3:[],10:[],11:[],20:[],21:[],41:[]}
    # for count in count_data:
    #     anchor_list.append(count['name'])
    #     for key in count_dict:
    #         if key in count['data'].keys():
    #             count_dict[key].append(count['data'][key]) 
    #         else:
    #             count_dict[key].append(0) 
    # print('count_dict',count_dict)
    for akey in data_Dict.keys():
        anchor_list.append(akey)
    # anchor_list=data_Dict.keys()
    for key in count_dict.keys():
        for akey in data_Dict.keys():
            # print(count_dict[key],data_Dict[akey][key])
            count_dict[key].append(data_Dict[akey][key])


    data_dict={'anchors':anchor_list,'data':count_dict}
    print("Item count",anchor_list)
    return {"code":200,"message":"success",'data':{'total':count,'items': data_dict}}
@timer
def Statistics(request: schemas.AbnormSearchTable, db: Session):
    sqltext=''
    search_dict={}
    
    for k,v in request:
        if v and v!=0:
            search_dict[k]=v             
        print(k,v)
    metro_name='abnorm_'+search_dict.pop('metro_name')
    print('=========================\n',search_dict)
    import time
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    # search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    # search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')
    for k,v in search_dict.items():
        if k=='timestamp_start':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k=='timestamp_end':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
                
        # if k=='timestamp':
        #     if v:
        #         sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '+metro_name+'.timestamp'+'<'+str(v+86400000)+' and '
        elif k=='direction':
            if len(v)>1:
                pass
            else:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k=='type':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sear_dict[k]=v
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)>1 and len(v)<5:
                for j in v:
                    sqltext=sqltext+metro_name+'.'+k+'='+str(j)+' or '
                    # print(sqltext)
                sqltext=sqltext.rstrip(' or ')
                sqltext+=' and '
                # print('ss',sqltext)
            else:
                pass
                
        elif k=='level':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)==2:
                # sear_dict[k]=v
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' or '+metro_name+'.'+k+'='+str(v[1])
            else:
                pass
              
        elif v and v!=0 :
            sqltext=sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext=sqltext.rstrip(' and ')
    print("sqltext:",sqltext)

    new_abnorm = type("new_abnorm", (models.baseAbnorm, models.Base), {"__tablename__":metro_name})
    items = db.query(new_abnorm.timestamp,new_abnorm.id,new_abnorm.value).filter(new_abnorm.type==10).filter(text(sqltext)).order_by(new_abnorm.timestamp).all() 
    print("items---len:",len(items))
    arcing_min=5
    arcing_max=1300
    new_list=[]
    item_x=0
    for item in items:
        item_x=item[2]
        if item[2]<arcing_min:
            item_x=arcing_min
        elif item[2]>arcing_max:
            item_x=arcing_max+item[2]%100
        new_list.append((item[0],item[1],item_x))  
    items=new_list
    if items:
        max_time=cover_time(items[0])
        plist=[]
        start_timestamp=items[0][0]
        end_timestamp=0
        i=0
        j=0
        for item in items:
            if item[0]>max_time:
                # print(item[0],max_time)
                plist.append((max_time,i,end_timestamp-start_timestamp,j))
                max_time=cover_time(item)
                i=item[2]
                j=1
            else:
                i=i+item[2]
                j=j+1
                end_timestamp=item[0]
        plist.append((max_time,i,end_timestamp-start_timestamp,j))
        # print("plist",plist)
        data_dict=[]
        for i in plist:
            data_dict.append({'timestamp':i[0],'value':i[1],'runtime_day':i[2],'count':i[3]})
        count=len(items)
        # print("blog",items,count,data_dict)
        return {"code":200,"msg":"success",'data':{'total':0,'items': data_dict}}
    else:
        return {"code":404,"msg":"Empty",'data':{'total':0,'items': []}}

@timer
def searchByDate(request: schemas.AbnormSearchDate, db: Session):
    sqltext=''
    search_dict={}
    for k,v in request:
        if v and v!=0:
            search_dict[k]=v             
        print(k,v)
    sqltext2=''
    metro_name='abnorm_'+search_dict.pop('metro_name')
    print('search_dict:',search_dict)
    for k,v in search_dict.items():
        if k=='timestamp_start':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '
        elif k=='timestamp_end':
            if v:
                sqltext=sqltext+metro_name+'.timestamp'+'<'+str(v)+' and '
        elif k=='direction':
            if len(v)>1:
                pass
            else:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        elif k=='type':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sear_dict[k]=v
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)>1 and len(v)<5:
                for j in v:
                    sqltext2=sqltext2+metro_name+'.'+k+'='+j+' or '
                    # print(sqltext)
                sqltext2=sqltext2.rstrip(' or ')
                sqltext2+=' and '
                # print('ss',sqltext)
            else:
                pass              
        elif k=='level':
            print(v)
            if len(v)==1:
                sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
                # sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
            elif len(v)==2:
                # sear_dict[k]=v
                sqltext2=sqltext2+metro_name+'.'+k+'='+v[0]+' or '+metro_name+'.'+k+'='+v[1]+' and '
            else:
                pass
              
        # if k=='timestamp':
        #     if v:
        #         sqltext=sqltext+metro_name+'.timestamp'+'>'+str(v)+' and '+metro_name+'.timestamp'+'<'+str(v+86400000)+' and '
        # elif k=='type' or k=='level' or k=='direction':
        #     print(v)
        #     if len(v)>1:
        #         sqltext=sqltext+metro_name+'.'+k+' IN '+str(tuple(v)).replace("'",'')+' and '
        #     else:
        # #         sqltext=sqltext+metro_name+'.'+k+'='+str(v[0])+' and '
        # elif v and v!=0 :
        #     sqltext=sqltext+metro_name+'.'+k+'='+str(v)+' and '
    sqltext=sqltext.rstrip(' and ')
    sqltext2=sqltext2.rstrip(' and ')
    print("sqltext:",sqltext)
    new_abnorm = type("new_abnorm", (models.baseAbnorm, models.Base), {"__tablename__":metro_name})
    items = db.query(
            new_abnorm.type,
        #    new_abnorm.id,
            func.count('*').label('value'),
            new_abnorm.timestamp,
            new_abnorm.level,
            # func.max(new_abnorm.timestamp).label('timestamp_max'),
            # func.min(new_abnorm.timestamp).label('timestamp_min'),
        ).filter(text(sqltext)).having(text(sqltext2)).group_by(new_abnorm.type).order_by(new_abnorm.timestamp).all()
#//////////////
    # count = db.query(new_abnorm).filter(text(sqltext)).count()  
    # items=items.all()
    # count=items.count()
    # items=db.query(new_abnorm.timestamp.cast( Datetime).label('t'),func.count('*').label('type_count'),new_abnorm.timestamp).filter(text(sqltext)).group_by('t').all()
    # items=db.query(func.count(new_abnorm.type).label('type_count'),func.year(new_abnorm.timestamp).label('y'),func.month(new_abnorm.timestamp).label('m'),func.day(new_abnorm.timestamp).label('d')).group_by('y','m','d').all()
    count=len(items)
    print("blog",items,count)
    return {"code":0,"msg":"success",'data':{'total':count,'items': items}}


def searchXG(request: schemas.AbnormSearchTable, db: Session):
    import time

    search_dict={}
    for k,v in request:
        if v and v!=0:
            search_dict[k]=v   
    timeArray0 = time.strptime(search_dict['timestamp'][0], "%Y-%m-%d")
    timeArray1 = time.strptime(search_dict['timestamp'][1], "%Y-%m-%d")
    # 转为时间戳
    search_dict['timestamp_start'] = int(time.mktime(timeArray0))*1000
    search_dict['timestamp_end'] = int(time.mktime(timeArray1))*1000
    search_dict.pop('timestamp')          
    print(search_dict)
    metro_name=search_dict.pop('metro_name')
    if '33' in metro_name:
        file_head='04033/'
    elif '32' in metro_name:
        file_head='04032/'
    else:
        file_head='010002/'
        
    print(metro_name)
    # search_dict.pop('type')
    FILE_PATH =config("FILE_PATH")+file_head
    items=[]
    new_items=[]
    date_file_list=[]
    for f in  os.listdir(FILE_PATH):
        if  f.startswith("20"):
            days=datetime.datetime.strptime(f, "%Y-%m-%d")
            timestamp = int(days.timestamp()*1000)
            if "timestamp_start" in search_dict.keys():
                if  timestamp>=search_dict['timestamp_start'] and timestamp<=search_dict['timestamp_end']:
                    date_file_list.append(f)
                else:
                    continue    
    for file_name in date_file_list:
        # print(file_name)
        file_name_now = os.path.join(FILE_PATH,file_name)
        files=os.listdir(file_name_now)
        for f in files:
            if f.startswith("xg-2") and f.endswith("jpg") and len(f)>30:
                print(f)
                timestamp=f[3:26]
                dt=datetime.datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S.%f")
                # print(dt.strftime('%Y-%m-%d %H:%M:%S'))
                timestamp = int(dt.timestamp()*1000)
                
                # a=f.index('!')
                b=f.index('(')
                c=f.index(')')
                d=f.index('[')
                e=f.index(']')
                direction=int(f[d+1:e])
                id_station_next=int(f[e+1:b])
                distance_from_last_station_m=float(f[b+1:c-2])*1000
                file_img=os.path.join(file_name+'/',f)
                items.append({'timestamp':timestamp,'direction':direction,'id_station_next':id_station_next,'distance_from_last_station_m':distance_from_last_station_m,
                'file_img':file_head+file_img})
                # print('***',timestamp,direction,id_station_next,distance_from_last_station_m,file_img)
    # print(items,len(items),search_dict)
    for item in items:
        print(item['id_station_next'])
    for item in items:
        print(item['id_station_next'])
        # print(search_dict)
        if "direction" in search_dict.keys() :
            if  item["direction"] in search_dict["direction"]:
                # items.pop(item)
                pass
            else:
                continue            
        if "timestamp_start" in search_dict.keys() :
            if  item['timestamp']>=search_dict['timestamp_start'] and item['timestamp']<=search_dict['timestamp_end']:
                pass
            else:
                continue     
                
        if "distance" in search_dict.keys() :
            # print(abs(item["distance_from_last_station_m"]-search_dict["distance"]))
            if  abs(item["distance_from_last_station_m"]-search_dict["distance"])<10:
                pass
            else:
                continue     
                
        if "id_station_next" in search_dict.keys() :
            if  item['id_station_next']>search_dict['id_station_pre'] and item['id_station_next']<=search_dict['id_station_next']:
                pass
            else:
                continue    
        item['anchor_name'],item['anchor_distance_m']=canchor.getAnchorName(item['direction'],item["id_station_next"],item['distance_from_last_station_m']) 
        new_items.append(item)    

    print(len(new_items))
    return {"code":200,"message":"success",'data':{'total':len(new_items),'items': new_items}}

def delXG(request:str):
    s=request.file_img.index(':88')
    print(request.file_img)
    print(request.file_img[s+4:])
    relatepath=request.file_img[s+4:]

    FILE_PATH =config("FILE_PATH")
    os.remove(FILE_PATH+relatepath)
    return {"code":200,"message":"success delete",'data':{}}

def cover_time(items):
    oneday=datetime.timedelta(days=1)
    time_max = datetime.datetime.strptime(datetime.datetime.fromtimestamp(items[0] / 1000).strftime("%Y-%m-%d"),"%Y-%m-%d")+oneday
    x_int = int(round(time_max.timestamp()))*1000
    # print(time_max,x_int)
    return x_int
def dual_val(val):
    if val<5:
        return 5
    elif val > 1300:
        return 1300+val%100
    else:
        return val


def get_all(db: Session):
    """
    Get all blogs

    Args:
        db (Session): Database session

    Returns:
        List[models.Blog]: List of blogs
    """
    new_abnorm = type('new_abnorm', (models.Abnorms,Base), {'__tablename__':'Abnorminfo2'})
    return db.query(new_abnorm).all()
    

def create(request: schemas.Abnorm, db: Session):
    """
    Create a new blog

    Args:
        request (schemas.Blog): Blog object
        db (Session): Database session

    Returns:
        models.Blog: Blog object
    """
    new_metro = models.Abnorm(
        timestamp= request.timestamp,
        id_station_dst=request.id_station_dst,
        id_station_next=request.id_station_next,
        velocity_km_per_h=request.velocity_km_per_h,
        distance_from_last_station_m= request.distance_from_last_station_m,#距上一站已驶出距离
        direction= request.direction,#上下行方向，1上行，-1下行，0未知
        id_tour= request.id_tour,#趟次,
        type = request.type,# 告警类型,
        level = request.level,# 等级,
        info= request.info,# 备注信息
        file_img= request.file_img,# 图像相对路径
        file_video = request.file_video,# 视频相对路径
        confirm= request.confirm#是否确认为故障，此字段可忽略
        )
    db.add(new_metro)
    db.commit()
    db.refresh(new_metro)
    return new_metro

# def search(request: schemas.AbnormSearchDate, db: Session):
#     # print(request)
#     sqltext=''
#     search_dict={}
#     for k,v in request:
#         if v and v!=0 :
#             search_dict[k]=v             
#         print(k,v)
#     print('==========',search_dict)

#     for k,v in search_dict.items():
#         if k=='timestamp_start':
#             sqltext=sqltext+'timestamp'+'>'+str(v)+' and '
#         elif k=='timestamp_end':
#             sqltext=sqltext+'timestamp'+'<'+str(v)+' and '
#         elif v and v!=0 :
#             sqltext=sqltext+k+'=='+str(v)+' and '
#     sqltext=sqltext.rstrip(' and ')
#     print(sqltext)
#     blog = db.query(models.Abnorm).filter(text(sqltext)).all()
#     print("blog",blog)
#     if blog:
#         return blog

#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Blog with the id {request.id_tour} is not available",
#         )


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
    blog_to_delete = db.query(models.Blog).filter(models.Blog.id == id)

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

