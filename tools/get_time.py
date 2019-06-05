#!/usr/bin/env python3
import time
import sys
import urllib.request
import json
import os

if __name__ == "__main__":
    try:
        # host = sys.argv[1]
        host = "10.252.97.88"
        resp = urllib.request.urlopen("http://{}/iotgw/api/v1/now".format(host))
        content = resp.read()
        serverTime = json.loads(content.decode('utf-8'), encoding='utf-8')
        tm = time.localtime(serverTime['data']['unixNano']/1000000000)
        os.system("date -s \"{:04}-{:02}-{:02} {:02}:{:02}:{:02}\"".format(*tm))
    except Exception as e:
        print("param invalid")
        sys.exit(1)
