#!/usr/bin/env python3
from uplink import Uplink
# from downlink import dl
# from task import task
import sys
import os
from epd_log import epdlog as LOG

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    LOG.info('epd service start...')
    uplinkHandler = Uplink()
    uplinkHandler.begin()
    uplinkHandler.end()
    
