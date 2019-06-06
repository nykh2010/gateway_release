import os
import json
import urllib

with os.popen("curl --form \"file=@/home/xulingfeng/project/gateway_release/update/web.tar.gz\" http://10.252.96.247:8090/api/upload") as postfp:
    resp = postfp.read()

resp_dict = json.loads(resp, encoding='utf-8')
print(resp_dict['data']['url'])

url = "http://10.252.97.88/iot/api/v1/remotectl/commands"
data = {
    "from": "iot_web_console",
    "to": [
        {
            "sn": "PC-XULINGFENG-XULINGFENG"
        },
    ],
    "command": "upgrade",
    "method": "",
    "body": {
        "type":"webfile",
        "downcmd":"wget %s" % resp_dict['data']['url'],
        "workdir":"/media",
        "script":"upgrade.sh"
    },
    "publishNow": True,
    "maxRetries": 3,
    "expires": 38400,
    "detached": True
}

data = json.dumps(data)

resp = urllib.request.urlopen(url, data.encode('utf-8'))
print(resp.read())