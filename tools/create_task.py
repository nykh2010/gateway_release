import urllib.request
import os
import base64
import json
import http
import time
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open("/home/xulingfeng/project/gateway_release/tools/data", "rb") as f:
    content = f.read() 
    res = base64.b64encode(content)

cur_time = time.time()
start_time = cur_time + 100
end_time = start_time + 3600
str_start_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(start_time))
str_end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(end_time))

headers = {
    'Content-Type':'application/json',
    # 'accept-encoding':'gzip,deflate'
}

data = {
    "start_time":str_start_time,
    "end_time":str_end_time,
    "image_data_id":random.randint(1,100),
    "image_data": res.decode('utf-8'),
    "iot_dev_list":[
        "0000000000000001",
        "0102030405060001"
    ],
    "gw_groups":["25"]
}
print(str_start_time+" "+str_end_time)
request_data = json.dumps(data).encode()

req = urllib.request.Request(r"http://10.252.97.88/iotgw/api/v1/tasks",data=request_data, headers=headers, method='POST')
# resp = urllib.request.urlopen("http://10.252.97.88/iotgw/api/v1/tasks",data=request_data)
resp = urllib.request.urlopen(req)
content = resp.read()
print(content)
