#!/usr/bin/env python3

# from downlink import dl
# from task import task
import sys
import os
from epd_log import epdlog as LOG

version = '1.0.0'

if __name__ == "__main__":
    with open('/etc/gateway/gwapp.version', 'w') as vfp:
        vfp.write(version)   

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    LOG.info('epd service start...')
    from uplink import Uplink
    uplinkHandler = Uplink()
    uplinkHandler.begin()
    uplinkHandler.end()
    
