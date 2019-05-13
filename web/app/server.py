from tornado.web import RequestHandler
from config import Config
from auth import auth
from tornado.log import app_log as LOG



class ServerHandler(RequestHandler):
    server = Config("server")
    gateway = Config("gateway")
    
    @auth
    def get(self):
        # print(dir(wifi))       
        self.render("server_setup.html", server=self.server, gateway=self.gateway)

    def post(self, method):
        if method == "update":
            ret = {}
            try:
                self.server.set_item('host', self.get_argument('host'))
                self.server.set_item('port', self.get_argument('port'))
                
                ret['status'] = 'success'
                self.server.save()
                self.gateway.save()
            except Exception as e:
                ret['status'] = 'failed'
                ret['err_msg'] = e.__repr__()
                LOG.error(e.__str__())
            self.write(ret)