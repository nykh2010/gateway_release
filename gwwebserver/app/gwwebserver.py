#!/usr/bin/env python3
import tornado.httpserver
from tornado import web, log
from tornado.web import RequestHandler
from tornado.options import define,options
import uuid
import os
import time
from socketserver import TCPServer,UDPServer,BaseRequestHandler
from queue import Queue
from threading import Thread
import re
import sys
from gateway import GatewayHandler
from auth import AuthHandler,LoginHandler,LogoutHandler
from log import LogHandler
from radio import RadioHandler
from server import ServerHandler
from wifi import WifiHandler
from setup import SetupHandler
from radio import RadioHandler
from status import StatusHandler
from configparser import ConfigParser

# define('port',default=8000,type=int)
# define('host',default='0.0.0.0',type=str)
define('log_to_stderr', type=bool, default=False)
define('log_file_prefix', type=str, default='/var/logs/web.log')
define('log_file_max_size', type=int, default=5 * 1000 * 1000)

class Config(ConfigParser):
    def __init__(self, path):
        super().__init__()
        self.read(path)
        self.path = path
    
    def save(self):
        with open(self.path, "w") as fp:
            self.write(fp)

def main():
    # print('%s start...' % __file__)
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        [
            (r'/',LoginHandler),   
            (r'/logout', LogoutHandler),         
            (r'/server/(.*?)',ServerHandler),
            (r'/server',ServerHandler),
            (r'/gateway/(.*?)/(.*?)',GatewayHandler),
            (r'/gateway/(.*?)',GatewayHandler),
            (r'/status', StatusHandler),
            (r'/status/(.*?)', StatusHandler),
            (r'/radio/(.*?)',RadioHandler),
            (r'/setup/(.*?)', SetupHandler),
            (r'/setup', SetupHandler),
            (r'/log', LogHandler),
            (r'/log/(.*?)', LogHandler),
            (r'/auth/(.*?)', AuthHandler),
            (r'/auth', AuthHandler),
            (r'/wifi/(.*?)', WifiHandler),
            (r'/wifi', WifiHandler),
            (r'/radio', RadioHandler)
        ],
        debug = True,
        static_path = os.path.join(os.path.dirname(__file__),"../static"),
        template_path = os.path.join(os.path.dirname(__file__),"../templates"),
        xsrf_cookies=True
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    conf = Config('/etc/gateway/system.ini')
    url = conf.get('com', 'web')
    url = url.split(':')
    httpServer.listen(url[1],url[0])
    log.app_log.info("start...")
    tornado.ioloop.IOLoop.instance().start()
    return 0
    # pwindows.join()

if __name__ == '__main__':
    if '--version' in sys.argv:
        print("v1.0.0")
        sys.exit(0)
    main()
