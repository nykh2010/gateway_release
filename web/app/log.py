from tornado.web import RequestHandler
from config import Config
from auth import auth
import os
import re

class LogMsg:
    __stack = []
    def __init__(self, name):
        self.__name = name
    
    def parse_record(self, record):
        ret = {
            "time":"",
            "msg":""
        }
        match_res = re.search(r"\[(.*?)\]-(.*)", record)
        ret['time'] = match_res.group(1)
        ret['msg'] = match_res.group(2)
        return ret

    def put(self, record):
        if len(self.__stack) > 10:
            return
        else:
            r = self.parse_record(record)
            self.__stack.append(r)
    
    def read(self, path):
        self.__stack.clear()
        with open(path, "r") as f:
            lines = f.readlines()
            if (len(lines) > 10):
                for record in lines[-10:]:
                    self.put(record)
            else:
                for record in lines:
                    self.put(record)
        return self.__stack

class LogHandler(RequestHandler):
    __logmsg = LogMsg("system")
    @auth
    def get(self, name=None):
        log = Config("log")
        if name is None:
            records = self.__logmsg.read(path=os.path.join(log.path, "epd.log"))
            self.render('log.html', records=records)
        else:
            records = self.__logmsg.read(path=os.path.join(log.path, "%s.log" % name))
            content = self.render_string('log_template.html', records=records)
            self.write(content)