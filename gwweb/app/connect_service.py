import os
import json
from socket import socket, AF_UNIX
from tornado.log import app_log as LOG

services = [
    ('serial', r'/var/run/serial.sock'),
    ('database', r'/var/run/sqlite3.sock')
]

def send_to_service(service_name, data=None, need_resp=True):
    path = ""
    if not isinstance(data, dict):
        return None
    for service in services:
        if service_name == service[0]:
            path = service[1]
            break
    if path:
        try:
            content = None
            client = socket(family=AF_UNIX)
            client.connect(path)
            content = json.dumps(data)
            client.send(content.encode('utf-8'))
            if need_resp:
                resp = client.recv(1024*1024)
                if not resp:
                    raise Exception()
                resp = resp.decode('utf-8')
                LOG.info(resp)
                content = json.loads(resp, encoding='utf-8')
        except Exception as e:
            LOG.error(e.__repr__())
            content = {
                'status':500,
                'msg':e.__repr__()
            }
        finally:
            client.close()
            return content

