from configparser import ConfigParser
import os
from epd_log import epdlog as LOG
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

# PATH = '/etc/gateway'

# class Config:
#     def __init__(self,name):
#         try:
#             self.__name = name
#             self.__config = ConfigParser()
#             self.__config.read(os.path.join(PATH, "%s.ini" % name))
#             for k,v in self.__config.items(name):
#                 self.__setattr__(k, v)
#         except Exception as e:
#             LOG.error(e.__repr__())
#             self.__config.add_section(self.__name)
#             self.save()
    
#     def set_item(self, name, value):
#         self.__setattr__(name, value)
#         self.__config.set(self.__name, name, value)
    
#     def save(self):
#         with open(os.path.join(PATH, "%s.ini" % self.__name), "w") as f:
#             self.__config.write(f)
