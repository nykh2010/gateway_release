from tornado.web import RequestHandler
from auth import auth
from config import Config
import os
import time
from tornado.log import app_log as LOG
from configparser import ConfigParser
from downlink import downlink
import os

class WifiHandler(RequestHandler):
    connect_path = '/home/xulingfeng/project/gateway_release/system/connect.py'
    def sent_cmd(self, cmd):
        with os.popen(cmd) as fp:
            res = fp.readlines()
        return res

    @auth
    def get(self):
        wifi = Config("wifi")
        ethernet = Config('ethernet')
        self.render("wifi_setup.html", wifi=wifi, eth=ethernet)
    
    def post(self, method):
        ret = {}
        if method == 'update':
            try:
                device = self.get_argument('device')
                if device == 'eth':
                    self.sent_cmd("%s -i ethernet --command set --mode %s --addr %s --netmask %s" % \
                        (self.connect_path, self.get_argument('mode'), self.get_argument('wire_address'), self.get_argument('wire_netmask')))
                    ret['status'] = 'success'
                else:
                    self.sent_cmd("%s -i wifi --command set --mode %s --ssid %s --psk %s" % \
                        (self.connect_path, 'sta', self.get_argument('sta_ssid'), self.get_argument('sta_passwd')))
                    ret['status'] = 'success'
            except Exception as e:
                LOG.error(e.__str__())
                ret['status'] = 'failed'
                ret['err_msg'] = "配置失败"
            finally:
                self.write(ret)