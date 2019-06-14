from configparser import ConfigParser
import os
from tornado.log import app_log as LOG
# import json

PATH = '/etc/gateway/system.ini'

class Config(ConfigParser):
    def __init__(self, name, path=PATH):
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

class Gateway(Config):
    def __init__(self):
        super().__init__("gateway")
        # gateway_config = self.confdict.gateway
        for k in self.options('gateway'):
            self.__setattr__(k, self.get('gateway', k))