#!/usr/bin/env python3
import os
import time
import sys
import threading
from configparser import ConfigParser


backup_base_path = r'/var/backups'


bin_path = None
config_path = None
need_reboot = False

os.chdir(os.path.dirname(os.path.abspath(__file__)))
timestamp = str(int(time.time()))
path_config = ConfigParser()
path_config.read('install.ini')          # 获取配置信息
if path_config.has_option('INSTALL', 'bin_path'):
    bin_path = path_config.get('INSTALL', 'bin_path')
if path_config.has_option('INSTALL', 'config_path'):
    config_path = path_config.get('INSTALL', 'config_path')
if path_config.has_option('INSTALL', 'need_reboot'):
    need_reboot = path_config.getboolean('INSTALL', 'need_reboot')

app_name = os.path.basename(bin_path)

def backup():
    '''备份'''
    cur_backup_path = os.path.join(backup_base_path, timestamp)
    os.system("mkdir -p %s" % cur_backup_path)
    if config_path:         # 备份原始配置文件
        os.system("mkdir %s" % os.path.join(cur_backup_path, 'config'))
        os.system("cp %s/* %s -rf" % (config_path, os.path.join(cur_backup_path, 'config')))
    if bin_path:            # 备份应用文件
        os.system("cp %s %s -rf" % (bin_path, cur_backup_path))

def rollback():
    '''回滚'''
    backup_path = os.path.join(backup_base_path, timestamp)
    os.chdir(backup_path)
    if config_path:
        os.system("cp %s/* %s -rf" % (os.path.join(backup_path, 'config'), config_path))
    os.system("cp %s %s -rf" % (app_name, os.path.dirname(bin_path)))

count = 10
def reboot():
    global count
    count = count - 1
    print("\rreboot after %d ......" % count)
    if count:
        th = threading.Timer(1, reboot)
        th.start()
    else:
        print("reboot now ......")
        os.system("reboot")

# 安装开始
try:
    print("install start ......")
    backup()
    print("backup complete")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))     # 切换至当前目录
    print("kill %s process" % app_name)
    os.system("/home/root/kill_process %s" % app_name)      # 杀死所有应用
    os.system("cp %s %s -rf" % (app_name, os.path.dirname(bin_path)))   # 拷贝应用程序
    if config_path:
        os.system("cp config/* %s -rf" % config_path)       # 拷贝配置文件
    print("copy complete")
    print("install complete ......")
    os.system("rm /var/backups/%s -rf" % timestamp)
    if need_reboot:
        print("\rreboot after 10 seconds")
        reboot()
    sys.exit(0)
except:
    rollback()
    sys.exit(1)
