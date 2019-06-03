from tornado.web import RequestHandler
from config import Config
from auth import auth
from tornado.log import app_log as LOG
import re
import os



class ServerHandler(RequestHandler):
    @auth
    def get(self):
        # print(dir(wifi))       
        server = Config("server")
        self.render("server_setup.html", server=server)

    def post(self, method):
        if method == "update":
            ret = {}
            try:
                host = self.get_argument('host')
                flag = re.match(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)', host)
                if flag is None:
                    raise Exception("ip地址非法")
                port = self.get_argument('port')
                if int(port) > 65536:
                    raise Exception("端口号非法")
                os.system('python3 /usr/local/bin/tools/server.py --host={} --port={}'.format(host, port))
                ret = {'status':'success'}
            except Exception as e:
                ret['status'] = 'failed'
                ret['err_msg'] = e.__str__()
                LOG.error(e.__str__())
            self.write(ret)