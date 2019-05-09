import tornado
from tornado.httpserver import HTTPServer
from tornado.web import Application
import tornado
from threading import Thread,Semaphore,RLock
from queue import Queue
import json
# from task import task
import os 
# from gateway import gateway
# from protocol import protocol
from protocol import TaskApp, RadioApp, GatewayApp
from configparser import ConfigParser
from epd_log import epdlog as LOG
import sys
import os
import urllib.request
import urllib.parse

sys.path.append(os.path.dirname(__file__))

token = r"MQRROJMAjKxaUy&kGMLoGc7YJDLLaiTu"

class Upload:
    def send(self, url, data):
        try:
            data = json.dumps(data).encode('utf-8')
            LOG.info(data)
            request = urllib.request.Request(url, data=data, headers={'token':token})
            resp = urllib.request.urlopen(request)
            content = resp.read().decode('utf-8')
            LOG.info("result:" + content)
            content = json.loads(content)
            return content
        except Exception as e:
            LOG.error(e.__str__())



    # def send(self, payload, topic='pc_test', wait_event=None, need_wait=False, cache=False):
    #     if cache:
    #         url = r'http://127.0.0.1:7788/mqtt/publish/offlinecache'
    #     else:
    #         url = r'http://127.0.0.1:7788/mqtt/publish'
    #     data = {}
    #     data['topic'] = topic
    #     data['payload'] = payload

    #     try:
    #         params = json.dumps(data).encode('utf-8')
    #         LOG.info(params)
    #         request = urllib.request.Request(url, data=params, headers={'token':token})
    #         resp = urllib.request.urlopen(request)
    #         content = resp.read().decode('utf-8')
    #         LOG.info("result:"+content)
    #     except Exception as e:
    #         LOG.error(e.__str__())
    
    # def send_remote(self, url, data):
    #     param = urllib.parse.urlencode(data)
    #     request_url = url + '?' + param
    #     opener = urllib.request.build_opener()
    #     req = urllib.request.Request(request_url)
    #     try:
    #         resp = opener.open(req, timeout=1)
    #         content = resp.read()
    #         content = json.loads(content)
    #         return content
    #     except Exception as e:
    #         LOG.error("%s request failed - %s", request_url, e.__str__())
    #         return None
            


app = Application(
    [
        (r'/task/(.*?)', TaskApp),        
        (r'/radio/(.*?)', RadioApp),      
        (r'/gateway/(.*?)', GatewayApp)
    ]
)

class Uplink(HTTPServer):
    global app
    def initialize(self):
        # get config file
        super().initialize(request_callback=app)
        self.__host = "0.0.0.0"
        self.__port = 5000
        
    def begin(self):
        LOG.info("sever host:%s port:%d", self.__host, self.__port)
        self.listen(self.__port, self.__host)
        tornado.ioloop.IOLoop.current(instance=False).start()

    def end(self):
        LOG.info("server stop")
        
    def send(self, payload):
        # upload data
        pass