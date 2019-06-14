import logging
import sys
import logging.handlers

Format = "[%(asctime)s]-%(filename)s:%(lineno)s %(message)s"

class EpdLogger(logging.Logger):
    def __init__(self, name='epd'):
        super().__init__(name)
        self.handler = logging.handlers.RotatingFileHandler('/var/logs/epd.log', maxBytes=5*1024*1024, backupCount=5)
        self.formater = logging.Formatter(fmt=Format)
        self.handler.setFormatter(self.formater)
        self.addHandler(self.handler)

epdlog = EpdLogger()
