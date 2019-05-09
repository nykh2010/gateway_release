#!/usr/bin/env python3
from configparser import ConfigParser
from socketserver import UnixStreamServer, StreamRequestHandler
from socket import socket, AF_UNIX
from threading import Thread
import json
import os
import time

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

class SetHandler:
    def func(self, data):
        ret = {}
        try:
            enable = data['enable']
            if enable == 'false':
                status = wifi.close_wifi()
                if status != 'success':
                    raise Exception('close wifi failed')
                else:
                    wifi.set_item('enable', enable)
                    wifi.save()
                    ret['status'] = status
            else:
                passwd = data['passwd']
                ssid = data['ssid']
                encryption = data['encryption']
                status = wifi.change_ssid_passwd(ssid, passwd)
                if status != 'success':
                    raise Exception('chang ssid & passwd failed')
                else:
                    wifi.set_item('sta_passwd', passwd)
                    wifi.set_item('sta_ssid', ssid)
                    wifi.set_item('encryption', encryption)
                    wifi.save()
                    ret['status'] = status
        except Exception as e:
            ret['status'] = 'error'
            ret['msg'] = e.__str__()
        finally:
            return ret

apps = [
    ('set', SetHandler),
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
        self.__path = self.wifi
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

class Wifi(Config):
    '''
        1. 启动wpa_supplicant
        wpa_supplicant -D nl80211 -i wlan0 -c /etc/wpa_supplicant.conf -B
        2. 禁用 network 0
        wpa_cli -iwlan0 disable_network 0
        3. 修改 ssid
        wpa_cli -iwlan0 set_network 0 ssid '"<ssid>"'
        4. 修改 psk
        wpa_cli -iwlan0 set_network 0 psk '"<psk>"'
        5. 保存 config
        wpa_cli -iwlan0 save_config
        6. 使能配置
        wpa_cli -iwlan0 enable_network 0
        7. 自动获取ip
        dhclient wlan0
    '''
    def __init__(self):
        super().__init__('wifi')

    def set_mode(self):
        if self.mode == 'ap':
            pass            # 设置为ap模式
        elif self.mode == 'sta':
            pass            # 设置为sta模式
        else:
            raise Exception("mode error")

    def change_mode(self, new_mode):
        try:
            if new_mode != self.mode:
                if new_mode not in ('ap', 'sta'):
                    raise Exception("new mode not in ap, sta")
                self.set_item('mode', new_mode)
                self.set_mode()
                self.save()
            else:
                pass
        except Exception as e:
            pass
    
    def check_wifi_ps_state(self, check_state):
        try_count = 10
        while try_count:
            with os.popen("ps | grep hostapd") as res:
                result = res.readlines()
            flag = False
            for text in result:
                if "grep hostapd" not in text:
                    flag = True         # 存在进程
                    break
            if flag != check_state:
                try_count = try_count - 1
                time.sleep(1)
                continue
            else:
                return True
        return False

    def change_ssid_passwd(self, ssid, passwd):
        # LOG.info("change ssid & passwd")
        os.system("/etc/init.d/hostapd restart")
        ret = self.check_wifi_ps_state(True)
        if ret:
            # LOG.info("change wifi ssid & passwd success")
            return 'success'
        else:
            # LOG.error("change wifi ssid & passwd failed")
            return 'failed'

    def close_wifi(self):
        # LOG.info("close wifi")
        os.system("/etc/init.d/hostapd stop")
        ret = self.check_wifi_ps_state(False)
        if ret:
            # LOG.info("close wifi success")
            return 'success'
        else:
            # LOG.error("close wifi failed")
            return 'failed'

wifi = Wifi()

if __name__ == "__main__":
    try:
        # wifi = Wifi()
        wifi.set_mode()
        downlink = Downlink()
        downlink.start_service()
        downlink.stop_service()
    except Exception as e:
        print(e.__repr__())