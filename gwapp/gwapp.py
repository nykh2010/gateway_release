#!/usr/bin/env python3
from uplink import Uplink
# from downlink import dl
# from task import task
import sys
import os
from epd_log import epdlog as LOG

version = '1.0.1'

if __name__ == "__main__":
    if '--version' in sys.argv:
        print(version)
        sys.exit(0)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    LOG.info('epd service start...')
    uplinkHandler = Uplink()
    uplinkHandler.begin()
    uplinkHandler.end()
    
