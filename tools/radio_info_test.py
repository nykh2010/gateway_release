import os
from socketserver import UnixStreamServer, StreamRequestHandler
from socket import socket, AF_UNIX
from threading import Thread
import json
import sys

class Downlink:
    __error = False
    services = [
        ('epd', r'/var/run/epdserver.sock'),
        ('database', r'/var/run/sqlite3.sock'),
        ('serial', r'/var/run/serial.sock')
    ]
    __path = r'/var/run/serial.sock'
    def __init__(self):
        pass

    def send_service(self, service_name, data, need_resp=True):
        path = ""
        for service in self.services:
            if service_name == service[0]:
                path = service[1]
                break
        if path:
            try:
                self.__client = socket(family=AF_UNIX)
                self.__client.connect(path)
                content = json.dumps(data)
                self.__client.send(content.encode('utf-8'))
                if need_resp:
                    resp = self.__client.recv(1024*1024)
                    if not resp:
                        raise Exception()
                    resp = resp.decode('utf-8')
                    print(resp)
                    content = json.loads(resp, encoding='utf-8')
            except Exception as e:
                print(e.__repr__())
                content = {
                    'status':500,
                    'msg':e.__repr__()
                }
            finally:
                self.__client.close()
                return content

dl = Downlink()
data = {
    "cmd":"report",
    "radio":1
}
content = dl.send_service('serial', data)
print(content)