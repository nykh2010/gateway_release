#!/usr/bin/env python3
from configparser import ConfigParser
from socketserver import UnixStreamServer, StreamRequestHandler
from socket import socket, AF_UNIX
from threading import Thread
import json
import os
import time
import re

PATH = '/etc/gateway/system.ini'

class Config(ConfigParser):
    def __init__(self, name):
        path = PATH
        super().__init__()
        self.read(path)
        self.path = path
        self.name = name
        self.reload()
        
    def set_item(self, name, value):
        self.set(self.name, name, value)
        self.reload()

    def reload(self):
        for k in self.options(self.name):
            self.__setattr__(k, self.get(self.name, k))

    def save(self):
        with open(self.path, "w") as fp:
            self.write(fp)

class EthernetHandler:
    def func(self, request):
        pass

class SetHandler:
    def func(self, request):
        device = request['device']
        if device == 'wifi':
            pass
        elif device == 'ethernet':
            ethernet = Ethernet()
            ethernet.set_mode(request['mode'], request['ip'], request['netmask'])
        else:
            raise Exception("no device")
        resp = {'status':'ok'}
        return resp

class GetHandler:
    def func(self, request):
        device = request['device']
        if device == 'wifi':
            pass
        elif device == 'ethernet':
            ethernet = Ethernet()
            resp = {'status': 'ok'}
            resp['mode'] = ethernet.get_mode()
            resp['ip'], resp['netmask'] = ethernet.get_inet()
        return resp

apps = [
    ('set', SetHandler),
    ('get', GetHandler)
]

class DownlinkServer(StreamRequestHandler):
    def route(self, data):     
        for app in apps:
            if data['cmd'] == app[0]:
                return app[1]
        return None
    def handle(self):
        data = self.request.recv(1024)
        data = data.decode('utf-8')
        data = json.loads(data, encoding='utf-8')
        # LOG.info("downlink recv: %s", data)
        HandleClass = self.route(data)
        handler = HandleClass()
        send_data = handler.func(data)
        if isinstance(send_data, dict):
            content = json.dumps(send_data)
            # LOG.info("downlink send: %s", content)
            self.wfile.write(content.encode('utf-8'))

class Downlink(UnixStreamServer, Config):
    __error = False
    services = []
    def __init__(self):
        Config.__init__(self, 'com')
        self.__path = self.ethernet
        for option in self.options('com'):
            service = (option, self.get('com', option))
            self.services.append(service)
        if os.path.exists(self.__path):
            os.unlink(self.__path)
        super().__init__(self.__path, DownlinkServer)
        self.__thread = Thread(target=self.start_service)
        self.__thread.start()

    def start_service(self):
        # LOG.info("downlink service start")
        self.serve_forever()

    def stop_service(self):
        # LOG.info("downlink service stop")
        self.server_close()
        self.__thread.join()

    def send_service(self, service_name, data, need_resp=False):
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

class Ethernet(Config):
    '''
    1. /etc/network/interfaces 中 eth0 默认为 dhcp 模式
    2. 启动后读取配置文件。mode为dhcp或static模式
    3. dhcp --> static
        ifconfig eth0 192.168.0.1 netmask 255.255.255.0
        /etc/init.d/dhcpd-server restart
    4. static --> dhcp
        /etc/init.d/dhcpd-server stop
        ifconfig eth0 down
        ifconfig eth0 up
    '''
    def __init__(self):
        super().__init__('ethernet')

    def send_cmd(self, cmd):
        with os.popen(cmd) as fp:
            res = fp.readlines()
        print("start: %s" % cmd)
        print(res)
        return res

    def set_dhcp_mode(self):
        res = self.send_cmd('/etc/init.d/dhcpd-server stop')
        res = self.send_cmd('ifconfig %s down' % self.inet)
        res = self.send_cmd('ifconfig %s up' % self.inet)
    
    def set_static_mode(self, inet4_addr, netmask):
        self.set_item('inet4_addr', inet4_addr)
        self.set_item('netmask', netmask)
        res = self.send_cmd('ifconfig %s %s netmask %s' % (self.inet, self.inet4_addr, self.netmask))
        res = self.send_cmd('/etc/init.d/dhcpd-server restart')
        self.save()

    def get_inet(self):
        res = self.send_cmd('ifconfig %s | grep inet\ addr' % self.inet)
        if res:
            content = res[0]
            match_res = re.match(r'inet addr:(.*\d+).*Mask:(.*).*?', content.strip())
            return match_res.groups()
        else:
            return "", ""

    def get_mode(self):
        return self.mode

    def set_mode(self, mode, *args):
        '''
        if mode is static, args = (inet4_addr, netmask)
        '''
        self.set_item('mode', mode)
        if mode == 'dhcp':
            self.set_dhcp_mode(*args)            # 设置为dhcp模式
        elif mode == 'static':
            self.set_static_mode(*args)         # 设置为static模式
        else:
            raise Exception("mode error")
        self.save()

    def change_mode(self, new_mode):
        try:
            if new_mode != self.mode:
                if new_mode not in ('dhcp', 'static'):
                    raise Exception("new mode not in ap, sta")
                self.set_item('mode', new_mode)
                self.set_mode()
                self.save()
            else:
                pass
        except Exception as e:
            pass
    

if __name__ == "__main__":
    try:
        downlink = Downlink()
        downlink.start_service()
        downlink.stop_service()
    except Exception as e:
        print(e.__repr__())