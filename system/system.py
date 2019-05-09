#!/usr/bin/env python3
from configparser import ConfigParser
import threading
import os

import logging
import sys
import logging.handlers

Format = "[%(asctime)s]-%(filename)s:%(lineno)s %(message)s"

class SysLog(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.handler = logging.handlers.RotatingFileHandler('/var/logs/system.log', maxBytes=5*1024*1024, backupCount=5)
        self.formater = logging.Formatter(fmt=Format)
        self.handler.setFormatter(self.formater)
        self.addHandler(self.handler)
LOG = SysLog('system')

PATH = '/etc/gateway/system.ini'

class Monitor:
    def __init__(self, conf, app):
        self.conf = conf
        self.app = app
        self.pid = []
    
    def start_daemon(self):
        LOG.info("%s daemon start", self.app)
        self.daemon()

    def start(self):
        self.cmd_line = self.conf.get('service', self.app)
        os.system("%s &" % self.cmd_line)

    def stop(self):
        for pid in self.pid:
            os.system("kill -9 %s" % pid)
        self.pid = []

    def restart(self):
        LOG.info("%s restart", self.app)
        self.stop()
        self.start()
        LOG.info("%s restart complete", self.app)
    
    def get_pid(self, app):
        cmd = "ps -axf | grep %s" % self.cmd_line
        with os.popen(cmd) as fp:
            results = fp.readlines()
            print(results)
            indexs = []
            for result in results:
                if "grep %s" % self.cmd_line not in result:
                    indexs.append(result)
            pids = [index.split(" ")[0] for index in indexs]
            if len(pids) > 1:
                # 异常处理
                self.pid = pids
                raise Exception("%s too more run" % self.app)
            else:
                return pids
    
    def exception_upload(self):
        # 异常上报
        pass

    def daemon(self):
        # 监控程序
        try:
            self.pid = self.get_pid(self.app)
            if not self.pid:
                raise Exception("%s not run" % self.app)
        except Exception as e:
            LOG.error(e.__str__())
            self.restart()
        finally:
            t = threading.Timer(20, self.daemon)
            t.start()

app_monitors = [
    ('default', Monitor)
]

def get_monitor(conf, app_name):
    c_monitor = None
    for app_monitor in app_monitors:
        if app_name == app_monitor[0]:
            c_monitor = app_monitor[1]
            break
    if c_monitor is None:
        c_monitor = Monitor
    return c_monitor(conf,app_name)
    

def app_routine(*args):
    conf = args[0]
    app = args[1]
    monitor = get_monitor(conf, app)
    monitor.start_daemon()

if __name__ == "__main__":
    conf = ConfigParser()
    conf.read(PATH)
    apps = conf.options('service')
    ths = []
    for app in apps:
        th = threading.Thread(target=app_routine, name="%s" % app, args=(conf, app))
        ths.append(th)
        th.start()
    for th in ths:
        th.join()
    