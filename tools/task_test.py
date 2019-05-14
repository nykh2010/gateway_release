from tornado.httpserver import HTTPServer
import tornado
from tornado.web import Application
from tornado.web import RequestHandler
import time

# class AssignHandler(RequestHandler):
#     def post(self):
#         data = {
#             "status": "ok",
#             "data": {
#                 "task_id": 2,
#                 "task_status": 1,
#                 "scheduled_start_time": "2019-05-08 15:25:25",
#                 "scheduled_end_time": "2019-05-08 15:45:25",
#                 "start_time": "",
#                 "end_time": "",
#                 "image_data_id": 2,
#                 "image_data_url": "http://localhost:8000/download/178c084476f2d503106e592ade376686",
#                 "image_data_md5": "178c084476f2d503106e592ade376686",
#                 "iot_dev_list_url": "http://localhost:8000/download/c0710d6b4f15dfa88f600b0e6b624077",
#                 "iot_dev_list_md5": "c0710d6b4f15dfa88f600b0e6b624077"
#             }
#         }
#         self.write(data)

# app = Application(
#     [
#         ('/iotgw/api/v1/tasks/gwtasks/assign', AssignHandler)
#     ]
# )

# class Uplink(HTTPServer):
#     global app
#     def initialize(self):
#         # get config file
#         super().initialize(request_callback=app)
#         self.__host = "127.0.0.1"
#         self.__port = 80
        
#     def begin(self):
#         self.listen(self.__port, self.__host)
#         tornado.ioloop.IOLoop.current(instance=False).start()

#     def end(self):
#         pass
        
#     def send(self, payload):
#         # upload data
#         pass

# up = Uplink()
# up.begin()

import os
from socketserver import UnixStreamServer, StreamRequestHandler
from socket import socket, AF_UNIX
from threading import Thread
import json
import sys

apps = [
    
]

class DownlinkServer(StreamRequestHandler):
    def route(self, data):
        for app in apps:
            if data['cmd'] == app[0]:
                return app[1]
        return None
    def handle(self):
        data = self.request.recv(1024)
        data = data.decode('utf-8')
        data = json.loads(data, encoding='utf-8')
        print("downlink recv: %s" % data)
        HandleClass = self.route(data)
        handler = HandleClass()
        send_data = handler.func(data)
        if isinstance(send_data, dict):
            content = json.dumps(send_data)
            print("downlink send: %s" % content)
            self.wfile.write(content.encode('utf-8'))


class Downlink(UnixStreamServer):
    __error = False
    services = [
        ('epd', r'/var/run/epdserver.sock'),
        ('database', r'/var/run/sqlite3.sock')
    ]
    __path = r'/var/run/serial.sock'
    def __init__(self):
        if os.path.exists(self.__path):
            os.unlink(self.__path)
        super().__init__(self.__path, DownlinkServer)
        self.__thread = Thread(target=self.start_service)
        self.__thread.start()

    def start_service(self):
        print("downlink service start")
        self.serve_forever()

    def stop_service(self):
        print("downlink service stop")
        self.server_close()
        self.__thread.join()

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

class Serial:
    dl = Downlink()
    task_id = 0
    task_status = 0
    data_id = 0
    start_time = 0
    end_time = 0
    def check(self):
        data = {
            'cmd':'heart',
            'device_id': '0102030405060001',
        }
        content = self.dl.send_service('epd', data)
        print(content)
    
    def online(self):
        data = {
            "cmd":"online",
            "device_id":"0102030405060001",
            "data_id":10,
            "battery":50,
            "interval":10
        }
        content = self.dl.send_service('epd', data)
        print(content)
        # print('task_id: ' + str(content['task_id']))
        # print('data_id: ' + content['data_id'])
        # print('start_time: ' + content['start_time'])
        # print('end_time: ' + content['end_time'])
        # self.task_id = content['task_id']
        # self.data_id = content['data_id']
        # self.start_time = content['start_time']
        # self.end_time = content['end_time']
    
    def task_start(self):
        data = {
            "cmd":"task",
            "task_id":self.task_id,
            "status": 2
        }
        content = self.dl.send_service('epd', data)
        print(content)

    def task_end(self):
        with open("/tmp/success", "w") as fp:
            fp.writelines(["0102030405060001"])
        with open("/tmp/fail", "w") as fp:
            fp.writelines([])
        data = {
            "cmd": "task",
            "task_id": 2,
            "status": 3
        }
        content = self.dl.send_service('epd', data)
        print(content)

serial = Serial()
serial.online()
# time.sleep(20)
# serial.task_start()
# time.sleep(20)
# serial.task_end()
# time.sleep(100)

