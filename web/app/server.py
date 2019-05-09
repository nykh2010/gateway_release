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
                self.server.set_item('auth_key', self.get_argument('key'))
                self.gateway.set_item('id', self.get_argument('gid'))
                self.gateway.set_item('mac', self.get_argument('gmac'))
                self.server.set_item('wireless', self.get_argument('wireless_enable'))
                if self.server.wireless == 'true':
                    self.server.set_item('ssid', self.get_argument('ssid'))
                    self.server.set_item('passwd', self.get_argument('passwd'))
                ret['status'] = 'success'
                self.server.save()
                self.gateway.save()
            except Exception as e:
                ret['status'] = 'failed'
                ret['err_msg'] = e.__repr__()
                LOG.error(e.__str__())
            self.write(ret)