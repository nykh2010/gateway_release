from config import Config
from socketserver import UnixStreamServer, StreamRequestHandler
from socket import socket, AF_UNIX
import json

class Downlink(UnixStreamServer):
    __error = False
    services = []
    def __init__(self):
        self.conf = Config('com')
        for option in self.conf.options('com'):
            service = (option, self.conf.get('com', option))
            self.services.append(service)

    def send_service(self, service_name, data, need_resp=True):
        path = ""
        for service in self.services:
            if service_name == service[0]:
                path = service[1]
                break
        if path:
            try:
                self.__client = socket(family=AF_UNIX)
                self.__client.connect(path)
                content = json.dumps(data)
                self.__client.send(content.encode('utf-8'))
                if need_resp:
                    resp = self.__client.recv(1024*1024)
                    if not resp:
                        raise Exception()
                    resp = resp.decode('utf-8')
                    # LOG.info(resp)
                    content = json.loads(resp, encoding='utf-8')
            except Exception as e:
                # LOG.error(e.__repr__())
                content = {
                    'status':500,
                    'msg':e.__repr__()
                }
            finally:
                self.__client.close()
                return content

downlink = Downlink()