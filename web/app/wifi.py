from tornado.web import RequestHandler
from auth import auth
from config import Config
import os
import time
from tornado.log import app_log as LOG
from configparser import ConfigParser
from downlink import downlink

class WifiHandler(RequestHandler):
    @auth
    def get(self):
        wifi = Config("wifi")
        self.render("wifi_setup.html", wifi=wifi)
    
    def post(self, method):
        ret = {}
        if method == 'update':
            try:
                send_data = {
                    "cmd":"set",
                    "enable": self.get_argument('enable'),
                    "ssid": self.get_argument('sta_ssid'),
                    "encryption": self.get_argument('encryption'),
                    "passwd": self.get_argument('sta_passwd')
                }
                status = downlink.send_service('wifi', send_data)
                if status['status'] == 'error':
                    raise Exception(status['msg'])                
            except Exception as e:
                LOG.error(e.__str__())
                ret['status'] = 'failed'
                ret['err_msg'] = "配置失败"
            finally:
                self.write(ret)