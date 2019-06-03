from tornado.web import RequestHandler
from auth import auth
import os
from config import Config

class StatusHandler(RequestHandler):
    def get_task_status(self):
        task_config = Config('epdtask', '/etc/gateway/epdtask.ini')
        return task_config
        

    @auth
    def get(self, *args, **kwargs):
        if args is None:
            self.render("info.html")
        else:
            ret = {}
            ret['task'] = self.get_task_status()
            self.write(ret)
            