import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
from datetime import datetime, timedelta
from pytz import timezone,utc

headers={
    'device': 'mobile',
    'deviceid': '0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
}

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
                    detail_url = "https://api.591.com.tw/tw/v1/house/rent/detail?id={}&isOnline=1".format(RID)

                    resp = requests.get(detail_url, headers=headers).json()
                    json_data = resp['data']
                    data['url']   = 'https://rent.591.com.tw/home/{}'.format(RID)
                    data['building_use']  = json_data['kind']
                    data['latitude']      = json_data['address']['lat']
                    data['longitude']     = json_data['address']['lng']
                    data['owner']         = json_data['linkInfo']['name']
                    data['mobile']        = json_data['linkInfo']['mobile'].replace('-','')
                    data['phone']         = json_data['linkInfo']['phone']

                    data['sex']           = "不限"
                    data['sexID']         = "0"
                    sex_info = [_ for _ in json_data['service']['notice'] if 'sex' in _.get('key')]
                    if sex_info:
                        data['sexID']     = sex_info[0]['key'].replace('sex_','')
                        data['sex']       = sex_info[0]['name']
                    data['title']         = json_data['title']
                    data['price']         = json_data['price']

                    data['address']       = json_data['address']['data']
                    data['posttime']      = ( datetime.fromtimestamp( int(json_data['favData']['posttime']) ) ).strftime("%Y-%m-%d %H:%M:%S")
                    output.append(data)
                    print(data)
    return output
