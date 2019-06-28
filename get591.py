import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
from datetime import datetime, timedelta
from pytz import timezone,utc

headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

def get591(page=2):
    output = []
    for region in ['1','3']: # 縣市,  1:台北 3:新北
        for kind in ['2','3']: # 類型,  2,3 獨立套房,分租套房
            url = 'https://rent.591.com.tw/index.php?module=search&action=rslist&is_new_list=1&type=1&searchtype=1&region={}&kind={}&order=posttime&orderType=desc'.format(region, kind)
            jd = requests.get(url).json()
            for pg in range(1,page+1):
                print( "region: {} kind: {}  {}/{}".format(region,kind,str(pg),str(page)) )
                time.sleep(0.5)
                pg_url = url+'&firstRow={}'.format(pg*20)

                resp = requests.get(pg_url).json()
                soup = BeautifulSoup(resp['main'], "lxml" )
                for item in soup.select('.shInfo'):
                    data = {}
                    RID = re.search(r'detail-(\d+).html', item.prettify()).group(1)
                    data['view_people'] = re.search(r'(\d+)人', item.select('.pattern')[0].text ).group(1)
                    detail_url= "https://m.591.com.tw/api.php?module=iphone&action=houseRecordNew&id=R{}&version=1".format(RID)

                    resp = requests.get(detail_url, headers=headers).json()
                    json_data = resp['data']
                    data['url']   = 'https://rent.591.com.tw/rent-detail-{}.html'.format(json_data['id'].lstrip('R'))
                    data['building_use']  = json_data['kind']
                    data['latitude']      = json_data['lat']
                    data['longitude']     = json_data['lng']
                    data['owner']         = json_data['linkman']
                    data['mobile']        = json_data['mobile'] 
                    data['phone']         = json_data['telephone']
                    data['sex']           = json_data['sex']
                    data['sexID']         = json_data['sexID']
                    data['title']         = json_data['title']
                    data['price']         = json_data['price']

                    lane                  = re.search(r'\d+巷', json_data['addr'])
                    alley                 = re.search(r'\d+弄', json_data['addr'])
                    lane_str              = lane.group() if lane else ""
                    alley_str             = alley.group() if alley else ""
                    data['address']       = json_data['region'] + json_data['section'] + json_data['street']+\
                                                lane_str + alley_str + json_data['new_addr_number'] + json_data['new_floor']
                    data['posttime']      = ( datetime.fromtimestamp( int(json_data['posttime']) )+timedelta(hours=8) ).strftime("%Y-%m-%d %H:%M:%S")
                    output.append(data)
    return output
