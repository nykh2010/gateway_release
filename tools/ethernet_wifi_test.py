from socket import socket, AF_UNIX
import json

path = '/var/run/eth.sock'

client = socket(family=AF_UNIX)
client.connect(path)

# 获取网卡信息
data = {
    'cmd':'get',
    'device':'ethernet'
}
content = json.dumps(data)
client.send(content.encode('utf-8'))
resp = client.recv(1024*1024)
print(resp)