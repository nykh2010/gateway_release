#!/usr/bin/env python3
from configparser import ConfigParser
from socketserver import UnixStreamServer, StreamRequestHandler
from socket import socket, AF_UNIX
from threading import Thread
import json
import os
import time
import re
import sys
import getopt

'''
    修改服务器连接地址
'''

def save_config(host, port):
    server_config = ConfigParser()
    server_config.read('/etc/gateway/system.ini')
    server_config.set('server', 'host', host)
    server_config.set('server', 'port', port)
    with open('/etc/gateway/system.ini', 'w') as fp:
        server_config.write(fp)
    with open('/etc/gateway/dma.ini', 'w') as fp:
        fp.write("mqttserver={}:{}".format(host, port))

def get_dma_pid():
    with os.popen("ps | grep -E 'dma.msghub$' | awk '{print $1}'") as fp:
        res = fp.readlines()
        return res[0]

def kill_process(pid):
    ret = os.system("kill -9 {}".format(pid))
    return ret

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    if sys.argv[1] == 'restart':
        pid = get_dma_pid()
        ret = kill_process(pid)
        sys.exit(ret)
    if sys.argv[1] == 'init':
        server_config = ConfigParser()
        server_config.read('/etc/gateway/system.ini')
        host = server_config.get('server', 'host')
        port = server_config.get('server', 'port')
        with open('/etc/gateway/dma.ini', 'w') as fp:
            fp.write("mqttserver={}:{}".format(host, port))
        pid = get_dma_pid()
        ret = kill_process(pid)
        sys.exit(ret)
    opts, args = getopt.getopt(sys.argv[1:], 'i:', longopts=['host=','port='])
    try:
        params = {}
        for opt, arg in opts:
            params[opt] = arg
        if 'host' in params.keys():
            save_config(host=params['--host'], port=params['--port'])
            pid = get_dma_pid()
            ret = kill_process(pid)
        else:
            raise Exception("params invalid")
    except Exception as e:
        print(e.__str__())        
        sys.exit(1)
    sys.exit(ret)
