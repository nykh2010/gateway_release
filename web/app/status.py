from tornado.web import RequestHandler
from auth import auth
import os
from config import Config

class StatusHandler(RequestHandler):
    def get_task_status(self):
        task_config = Config('epdtask', '/etc/gateway/epdtask.ini')
        return task_config
    
    def get_inet_status(self):
        with os.popen("python3 /usr/local/bin/tools/connect.py -i ethernet --command get") as fp:
            res = fp.readlines()
        eth0 = res[1].split(':')[1]
        with os.popen("python3 /usr/local/bin/tools/connect.py -i wifi --command get") as fp:
            res = fp.readlines()
        wifi = res[-2].split(':')[1]
        return eth0, wifi
    
    def get_radio_status(self):
        pass

    def get_system_status(self):
        pass
        

    @auth
    def get(self, method=None):
        if method is None:
            task = self.get_task_status()
            eth0, wifi = self.get_inet_status()
            wan = dict(inet_addr=eth0)
            wan['interface'] = 'eth0'
            lan = dict(inet_addr=wifi)
            lan['interface'] = 'wlan0'
            self.render("info.html", task=task.__dict__, wan=wan, lan=lan)
        else:
            ret = {}
            ret['task'] = self.get_task_status()
            self.write(ret)
            