from random import randint
from time import time, strptime, mktime, localtime
from config import Config
import uplink
from downlink import dl
import threading
import hashlib
from epd_log import epdlog as LOG
from task import EpdTask
import os
import urllib.request
import json


STEP_TIME = 20*60       # 任务间隔时间
handler_interval = 10   # 10秒产生一次定时任务
DEFAULT_KEY = 8888      # 默认key

class Gateway(Config):
    # 网关参数
    key = None
    __taskId = 0
    __taskStatus = 0
    __whiteListMD5 = ""
    __whitelist = set()
    pending_list = set()
    def __init__(self):
        super().__init__('gateway')
        # 启动定时任务
        self.interval_timing()
        self.__whiteListMD5 = self.get_whitelist()
        self.__taskId = self.get_task_id()
        self.__taskStatus = self.get_task_status()
        self.key = self.get_auth_key()
        self.set_task_monitor()
        timer = threading.Timer(handler_interval, self.timer_handler)
        timer.start()

    def get_whitelist(self):
        try:
            with open(self.white_list_url, 'rb') as whitelistfile:
                content = whitelistfile.read()
                self.__whitelist = set(content.decode('utf-8').split('\n'))
                hash_obj = hashlib.md5()
                hash_obj.update(content)
                return str(hash_obj.hexdigest())
        except Exception as e:
            LOG.error("get white list failed: %s" % e.__str__())
            return ""

    def create_whitelist(self, url, md5):
        LOG.info("download white list file")
        os.system("rm %s.tmp" % self.white_list_url)        #####
        os.system("wget -c %s -O %s.tmp" % (url, self.white_list_url))
        ret = self.check_whitelist_integrity(md5)
        if not ret:
            return False
        else:
            LOG.info("store white list file")
            os.system("mv %s.tmp %s" % (self.white_list_url, self.white_list_url))
            self.__whiteListMD5 = self.get_whitelist()
            return True

    def create_pending_list(self):
        self.pending_list.clear()

    def save_pending_list(self):
        with open('/tmp/pending', 'w') as fp:
            fp.writelines([device+'\n' for device in self.pending_list])

    def add_pending_list(self, device_id):
        self.pending_list.add(device_id)

    def get_pending_list(self):
        return self.pending_list

    def get_failed_list(self, success_list):
        success_list = set(success_list)
        return list(self.pending_list - success_list)
    
    def check_whitelist_integrity(self, md5):
        hash_obj = hashlib.md5()
        with open("%s.tmp" % self.white_list_url, "rb") as whitelistfile:
            hash_obj.update(whitelistfile.read())
            hash_code = hash_obj.hexdigest()
        if md5 != hash_code:
            return False
        return True

    def is_in_whitelist(self, device_id):
        return device_id in self.__whitelist

    def is_in_executelist(self, device_id, data_id):
        epd_task = EpdTask(self.task_url)
        if self.__taskStatus not in ('1','2'):
            return False
        if epd_task.image_data_id == data_id:
            return False
        if not epd_task.is_in_executelist(device_id):
            return False
        return True
    
    def create_task(self, task_id, image_data_id, image_data_url,\
            image_data_md5, iot_dev_list_md5, iot_dev_list_url, start_time, end_time):
        epd_task = EpdTask(self.task_url)

        # 0-none 1-sleep 2-ready 3-run 4-finish 5-suspend
        if self.__taskId == 0 or (self.__taskStatus in ('','0','4','5')):
            # 下载任务
            os.system("wget %s -O %s.tmp" % (image_data_url, epd_task.data_url))
            os.system("wget %s -O %s.tmp" % (iot_dev_list_url, epd_task.execute_url))
            ret = self.check_task_integrity(image_data_md5, iot_dev_list_md5)
            if not ret:
                return False
            # 保存任务状态
            epd_task.set_item('task_id', str(task_id))
            epd_task.set_item('image_data_id', str(image_data_id))
            epd_task.set_item('image_data_url', image_data_url)
            epd_task.set_item('start_time', start_time)
            epd_task.set_item('end_time', end_time)
            epd_task.set_item('task_status', '1')
            epd_task.save()
            # 保存待更新列表
            os.system("mv %s.tmp %s" % (epd_task.data_url, epd_task.data_url))
            os.system("mv %s.tmp %s" % (epd_task.execute_url, epd_task.execute_url))
            self.__taskId = self.get_task_id()
            self.__taskStatus = self.get_task_status()     # 更新任务状态
            self.set_task_monitor()
            return True
        else:
            LOG.info("task status not allowed, status:%s", self.__taskStatus)
            return False

    def cancel_task(self, task_id):
        if self.__taskId != task_id:
            return False
        epd_task = EpdTask(self.task_url)
        epd_task.set_item('task_status', '0')
        epd_task.set_item('task_id', '0')
        epd_task.save()
        self.__taskId = self.get_task_id()
        self.__taskStatus = self.get_task_status()     # 更新任务状态
        return True

    def set_task_monitor(self):
        try:
            task_status = self.get_task_status()
            if task_status == '0':
                return
            start_time, end_time = self.get_task_time()
            end_time = mktime(strptime(end_time, "%Y-%m-%d %H:%M:%S"))
            cur_time = time()
            task_id = self.get_task_id()
            if task_status != '4' and (cur_time > end_time+60):     # 结束1分钟之后没有收到结束信号就主动结束
                LOG.info("task %s execute timeout", task_id)
                self.set_task_status(task_id, '4')
                self.report_task_status()
            elif task_status == '4':
                pass
            else:
                timer = threading.Timer(60, self.set_task_monitor)
                timer.start()
        except:
            pass

    def interval_timing(self):
        try:
            host = self.get('server', 'host')
            resp = urllib.request.urlopen("http://{}/iotgw/api/v1/now".format(host))
            content = resp.read()
            serverTime = json.loads(content.decode('utf-8'), encoding='utf-8')
            tm = localtime(serverTime['data']['unixNano']/1000000000)
            os.system("date -s \"{:04}-{:02}-{:02} {:02}:{:02}:{:02}\"".format(*tm))
        except Exception as e:
            LOG.error(e.__str__())
        finally:
            timer = threading.Timer(3600, self.interval_timing)
            timer.start()


    def report_task_status(self):
        data = {
            'topic': 'gateway/report/task/status',
            "payload": {
                "d": {
                    'task_id': int(self.__taskId),
                    'status': int(self.__taskStatus),
                    'success_list': [],
                    'failed_list': list(self.pending_list)
                }
            }
        }
        upload = uplink.Upload()
        upload.send('http://127.0.0.1:7788/mqtt/publish/offlinecache', data)

    def set_task_status(self, task_id, task_status):
        if self.__taskId != task_id:
            return False
        epd_task = EpdTask(self.task_url)
        epd_task.set_item('task_status', str(task_status))
        epd_task.set_item('task_id', str(task_id))
        epd_task.save()
        self.__taskId = self.get_task_id()
        self.__taskStatus = self.get_task_status()     # 更新任务状态
        return True

    def check_task_integrity(self, image_data_md5, iot_dev_list_md5):
        hash_obj = hashlib.md5()
        epd_task = EpdTask(self.task_url)
        with open("%s.tmp" % epd_task.data_url, "rb") as datafile:
            hash_obj.update(datafile.read())
            hash_code = hash_obj.hexdigest()
        if image_data_md5 != hash_code:
            LOG.info("image data md5 check failed")
            return False
        
        hash_obj = hashlib.md5()
        with open("%s.tmp" % epd_task.execute_url, "rb") as devfile:
            hash_obj.update(devfile.read())
            hash_code = hash_obj.hexdigest()
        if iot_dev_list_md5 != hash_code:
            LOG.info("iot dev list md5 check failed")
            return False
        return True

    def get_gw_id(self):
        with open('/etc/gateway/sn', 'r') as fp:
            sn = fp.readline()
        return sn.rstrip('\n')

    def get_task_id(self):
        epd_task = EpdTask(self.task_url)
        return int(epd_task.task_id)

    def get_task_status(self):
        epd_task = EpdTask(self.task_url)
        return epd_task.task_status

    def get_server_url(self):
        with os.popen("cat /etc/gateway/dma.ini | cut -f2 -d\"=\"", 'r') as fp:
            url = fp.read().strip()
        url = url.split(':')
        return url[0], url[1]       # host, port

    def get_task_time(self):
        epd_task = EpdTask(self.task_url)
        return epd_task.start_time, epd_task.end_time
        # return epd_task.
    
    def get_data_id(self):
        epd_task = EpdTask(self.task_url)
        return epd_task.image_data_id

    def get_interval_time(self):
        return self.interval

    def set_interval_time(self, interval_time):
        self.set_item('interval', interval_time)
        self.save()
    
    def get_auth_key(self):
        # 从文件中获取auth_key
        try:
            if self.key is None:
                with open(self.key_url, 'r+') as fp:
                    self.key = fp.read()
                    if not self.key:
                        fp.write(str(DEFAULT_KEY))
                        self.key = str(DEFAULT_KEY)
        except:
            self.set_auth_key(DEFAULT_KEY)
        return self.key

    def set_auth_key(self, key):
        self.key = None
        with open(self.key_url, 'w+') as fp:
            fp.write(str(key))
        self.key = self.get_auth_key()
        return self.key
    
    def timer_handler(self, args=None):
        '''
            定时任务
        '''
        data = {
            'topic': 'gateway/report/status',
            "payload": {
                "d": {
                    'task_id': self.__taskId,
                    'whitelist_md5': self.__whiteListMD5,
                    'check_code': int(self.key),
                    'interval': self.interval
                }
            }
        }
        upload = uplink.Upload()
        upload.send('http://127.0.0.1:7788/mqtt/publish/offlinecache', data)
        timer = threading.Timer(handler_interval, self.timer_handler)
        timer.start()

    try_count = 5
    def try_handler(self, service_name, data):
        ret = dl.send_service(service_name, data, need_resp=True)
        if ret['status'] != 'ok':
            if self.try_count:
                t = threading.Timer(5, self.try_handler, args=(service_name, data))
                t.start()
                self.try_count = self.try_count - 1
            else:
                LOG.error('%s service lost connection', service_name)

    def set_try_data(self, service_name, data):
        self.try_count = 5
        t = threading.Timer(5, self.try_handler, args=(service_name, data))
        t.start()

gw = Gateway()
