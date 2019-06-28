import pandas as pd
import requests
import time
import sys
import os
import re
import math
from pytz import timezone
from datetime import datetime

def _LR_dist(lat, diff_dist):
    if lat<0 or lat>90: return 'Wrong Latitude'
    deg_lat=(lat/180)*math.pi
    dist_per_deg = 111.32*math.cos( deg_lat ) # km/degree
    return diff_dist/dist_per_deg

def _UD_dist(lng, diff_dist):
    return diff_dist/110.574

def _coord_range(lat, lng, dist):
    LRdiff = _LR_dist(lat , dist)
    UDdiff = _UD_dist(lng, dist)
    return {
        'L':lng-LRdiff, 'R':lng+LRdiff,
        'U':lat+UDdiff, 'D':lat-UDdiff,
    }

def _fp(x):
    xx = int( re.search(r'\d+', x['price'].replace(',','') ).group(0) )
    return xx

def _getHouse(lat, lng, dist, price, item_list):
    doc=[]
    Co = _coord_range(lat, lng, dist)
    for obj in item_list:
        Long = ( float(obj['longitude']) > Co['L']) and ( float(obj['longitude']) < Co['R'])  # 左右
        Lat = ( float(obj['latitude']) > Co['D']) and ( float(obj['latitude']) < Co['U']) # 上下
        if Lat and Long:
            data={}
            data['title'] = obj['title']
            data['url'] = obj['url']
            data['address'] = obj['address']
            data['building_use'] = obj['building_use']
            data['price'] = obj['price']
            data['owner'] = obj['owner']
            data['phone'] = obj['phone']
            data['mobile'] = obj['mobile'].split(',')[0]
            data['view_people'] = obj['view_people']
            data['posttime'] = obj['posttime']
            data['sex'] = obj['sex']
            doc.append(data)
    return list( filter(lambda x: _fp(x)<price, doc ) )

def _tm(x):
    # 2019-06-22 15:06:04
    pattern = '%Y-%m-%d %H:%M:%S'
    tm_str = re.search(r'\d+-\d+-\d+ \d+:\d+:\d+', x['posttime']).group(0)
    return timezone('GMT+0').localize(datetime.strptime(tm_str, pattern))

def _sort_obj_index(data):
    return pd.DataFrame( data ).apply(_tm, 1).sort_values(ascending=False).index




### main function
def LineNotify(msg, TOKEN):
    token = TOKEN
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type" : "application/x-www-form-urlencoded",
    }
    payload = {'message': msg,}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code


def sendLineNotify(item_list, lat, lng, dist, price, n_items, location, TOKEN):
    data = _getHouse(lat, lng, dist, price, item_list)
    if not data: return None
    _index = _sort_obj_index(data)
    data1 = pd.DataFrame( data ).iloc[ _index[:n_items] ]
    data_segment = [data1[x:x+3] for x in range(0, len(data1), 3) ]
    _number = 1
    for dd in data_segment:
        msg="{} {}/{}\n".format(location, _number, len(data_segment) )
        for d in dd.iterrows():
            d = d[1].to_dict()
            msg+="""
標題: {}\n網址: {}\n價錢: {}\n房東: {}
地址: {}\n手機: {}\n已看: {}\n刊登時間: {}
=======================
                """.format(d['title'],d['url'],d['price'],d['owner'],\
                        d['address'],d['mobile'],d['view_people'],d['posttime'])
        LineNotify(msg, TOKEN)
        _number+=1
