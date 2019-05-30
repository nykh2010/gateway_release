from threading import Thread
import json
from time import time, sleep
from configparser import ConfigParser
from epd_log import epdlog as LOG
import sys
import os
# import task
import uplink
from downlink import dl
import time
from gateway import gw
import hashlib
from epd_exception import EpdException

sys.path.append(os.path.dirname(__file__))

# 下行协议
class Handle:
    def func(self):
        pass
    
    def upload(self, topic, data):
        up = uplink.Upload()
        url = r'http://127.0.0.1:7788/mqtt/publish'
        payload = {
            'topic': topic,
            'payload': data
        }
        up.send(url, payload)

class HeartRequest(Handle):
    def func(self, request):
        LOG.info('%s heart beat', request['device_id'])
        if gw.is_in_whitelist(request['device_id']):
            LOG.info("%s is in white list", request['device_id'])
            status = "ok"
        else:
            status = "error"
        send_data = {
            "status":status
        }
        return send_data

class RegisterRequest(Handle):
    def func(self, request):
        device_id = request['device_id']
        LOG.info("%s register", device_id)
        ret = gw.is_in_whitelist(device_id)
        send_data = {}
        if ret:
            LOG.info("%s is in white list", device_id)
            send_data['status'] = 'ok'
            send_data['key'] = int(gw.get_auth_key())
        else:
            send_data['status'] = 'error'
        return send_data

class OnlineRequest(Handle):
    def query_task(self, url, data):
        up = uplink.Upload()
        ret = up.send(url, data)
        return ret

    def func(self, request):
        try:
            send_data = dict()
            upload_data = None
            device_id = request['device_id']
            firmware = request.get('firmware', None)
            data_id = request.get('data_id', "0")
            interval = request.get('interval', None)
            if firmware:
                # 注册上报
                LOG.info("%s register", device_id)
                upload_data = {
                    "d": [{
                        "nid": device_id,
                        "d":{
                            "firmware": firmware
                        }
                    }]
                }
                topic = 'dma/report/periph/reg'
            elif data_id:
                # 心跳上报
                # 准备上报数据
                upload_data = {
                    "d": [{
                        "nid": device_id,
                        "d":{
                            "image_data_id": int(data_id),
                            "interval": request['interval'],
                            "battery": request['battery']
                        }
                    }]
                }
                topic = 'dma/report/periph'
                ts = gw.get_task_status()
                LOG.info("task status: %s", ts)
                if ts in ('0','4','5'): # 没有任务或任务已结束
                    data = {
                        'nid': device_id,
                        # 'image_data_id': int(data_id),
                        'image_data_id': int(gw.get_data_id()),
                        'sn': gw.get_gw_id()
                    }
                    LOG.info("start query")
                    resp = self.query_task('http://10.252.97.88/iotgw/api/v1/tasks/gwtasks/assign', data)
                    LOG.info("get response")
                    if resp:
                        # 应答成功，保存任务状态，下发时间，下载任务
                        if resp['status'] != 'ok':
                            raise Exception("get task error")
                        data = resp['data']
                        ret = gw.create_task(data['task_id'], data['image_data_id'], data['image_data_url'], \
                                data['image_data_md5'], data['iot_dev_list_md5'], data['iot_dev_list_url'], \
                                data['scheduled_start_time'], data['scheduled_end_time'])
                        if ret:
                            start_time, end_time = gw.get_task_time()
                            send_data['task_id'] = gw.get_task_id()
                            send_data['data_id'] = gw.get_data_id()
                            send_data['start_time'] = start_time
                            send_data['end_time'] = end_time

                            # 向serial发送任务开始命令
                            task_start = {
                                "cmd":"task",
                                "method":"create",
                                "task_id":send_data['task_id'],
                                "data_id":send_data['data_id'],
                                "start_time":send_data['start_time'],
                                "end_time":send_data['end_time']
                            }
                            ret = dl.send_service('serial', task_start, need_resp=True)
                            if ret['status'] != 'ok':
                                gw.set_try_data('serial', task_start)

                            # 添加待执行表
                            gw.create_pending_list()
                            gw.add_pending_list(device_id)
                        else:
                            # 创建失败上报
                            pass
                    else:
                        raise Exception("server no response")
                elif ts in ('1','2'):
                    ret = gw.is_in_executelist(device_id, data_id)
                    if ret:
                        start_time, end_time = gw.get_task_time()
                        send_data['task_id'] = gw.get_task_id()
                        send_data['data_id'] = gw.get_data_id()
                        send_data['start_time'] = start_time
                        send_data['end_time'] = end_time
                        gw.add_pending_list(device_id)
                else:
                    # 其他情况处理
                    pass
                # 更新唤醒周期
                send_data['status'] = 'ok'
                interval_time = gw.get_interval_time()
                if interval_time != request['interval']:
                    send_data['interval'] = interval_time
            else:
                raise Exception("request param invalid")
        except Exception as e:
            send_data['status'] = 'error'
            LOG.error(e.__repr__())
        finally:
            if upload_data:
                self.upload(topic, upload_data)
            return send_data
    
    def upload(self, topic, data):
        # 上传信息
        super().upload(topic, data)
        # super().upload('dma/report/periph', data)

class TaskRequest(Handle):
    def func(self, data):
        task_id = data['task_id']
        status = data['status']
        send_data = {}
        try:
            ret = gw.set_task_status(task_id, status)
            if not ret:
                raise Exception('task %d not exist' % task_id)
            upload_data = {}
            if status == 4:
                with open("/tmp/success") as successfile:
                    content = successfile.read()
                    success_list = content.split('\n')
                # with open("/tmp/fail") as failfile:
                #     content = failfile.read()
                #     fail_list = content.split('\n')
                os.unlink('/tmp/success')       # 删除文件
                # os.unlink('/tmp/fail')
                upload_data['success_list'] = success_list
                upload_data['failed_list'] = gw.get_failed_list(success_list)
            elif status == 3:
                # 保存待执行列表到文件
                gw.save_pending_list()
            else:
                pass            
            # 上传执行状态
            upload_data['task_id'] = task_id
            upload_data['status'] = status
            self.upload('gateway/report/task/status', upload_data)
            send_data['status'] = 'ok'
        except Exception as e:
            LOG.error(e.__str__())
            send_data['status'] = 'error'
            send_data['msg'] = e.__str__()
        finally:
            return send_data
    
    def upload(self, topic, data):
        send_data = {
            "d":data
        }
        super().upload(topic, send_data)

apps = [
    ("heart", HeartRequest),
    ("register", RegisterRequest),
    ("online", OnlineRequest),
    ("task", TaskRequest)
]

from tornado.web import RequestHandler
# from tornado.httpserver import HTTPServer
from tornado.web import HTTPError
# 上行接口
class TaskApp(RequestHandler):
    def post(self, cmd):
        try:
            request = self.request.body.decode('utf-8')
            request = json.loads(request)
            body = request['d']
            if cmd == 'create':
                pass
                # ret = gw.create_task(body['task_id'], body['image_data_id'], body['image_data_url'], \
                #     body['image_data_md5'], body['iot_dev_list_md5'], body['iot_dev_list_url'], \
                #     body['start_time'], body['end_time'])
                # if ret:
                #     data = {
                #         "cmd":"task",
                #         "method":"create",
                #         "task_id":body['task_id'],
                #         "data_id":body['image_data_id'],
                #         "start_time":body['start_time'],
                #         "end_time":body['end_time']
                #     }
                #     ret = dl.send_service('serial', data, need_resp=True)
                #     if ret['status'] != 'ok':
                #         gw.set_try_data('serial', data)
                #     # raise HTTPError(200)
                #     status = 'ok'
                #     msg = "task_id %s create success" % body['task_id']
                # else:
                #     # 不可创建任务
                #     LOG.info("task could not create")
                #     status = 'failed'
                #     msg = "task_id %s create not allowed" % body['task_id']
                #     # 上传命令处理结果
                # upload = uplink.Upload()
                # resp = {
                #     "id": request['id'],
                #     "from": request['from'],
                #     "status": status,
                #     "command": request['command'],
                #     "d":{
                #         "code":"task_status",
                #         "msg":msg
                #     }
                # }
                # # gw.get_task_status()
                # upload.send(resp, topic='dma/cmd/resp')
            elif cmd == 'cancel':
                # cancel task
                data = {
                    "cmd":"task",
                    "method":"cancel",
                    "task_id":body['task_id']
                }
                ret = dl.send_service('serial', data, need_resp=True)
                if ret['status'] != 'ok':               # 向模块发出取消命令
                    gw.set_try_data('serial', data)  

                ret = gw.cancel_task(body['task_id'])
                if ret:
                    status = 'ok'
                    result = {'result':'ok'}
                    try:
                        os.unlink("/tmp/success")
                        os.unlink("/tmp/fail")
                    except:
                        pass
                else:
                    status = 'err'
                    result = {'code':'cancel_failed', 'msg':'task not found'}
                # 上传处理结果
                upload = uplink.Upload()

                resp = {
                    "id": request['id'],
                    "from": request['from'],
                    "status": status,
                    "command": request['command'],
                    "msg":result
                }

                upload_data = {
                    'topic': 'dma/cmd/resp',
                    'payload': resp
                }

                upload.send('http://127.0.0.1:7788/mqtt/publish/offlinecache', upload_data)
            elif cmd == 'confirm':
                pass
                # confirm task 
                # data = {
                #     "table_name":"sql",
                #     "sql_cmd":"update `task` set (`start_time`='%s', `end_time`='%s', `status`=2) where `task_id`='%s';" % \
                #         (body['start_time'], body['end_time'], body['task_id'])
                # }
                # dl.send_service('database', data)
            else:
                raise HTTPError(404)
        except Exception as e:
            self.write(e.__str__())
            LOG.error("%s" % e.__str__())

class RadioApp(RequestHandler):
    def post(self, cmd):
        body = self.request.body.decode('utf-8')
        body = json.loads(body)
        src = "local" if body['from'] == 'local' else 'remote'
        radio_number = body.get('radio_number')
        if cmd == 'update':
            LOG.info('%s setup radio parameters', src)
            data = {
                "cmd":"update",
                "radio":radio_number
            }
        elif cmd == 'restart':
            LOG.info('%s restart radio', src)
            data = {
                "cmd":"restart",
                "radio":radio_number
            }
            ret = dl.send_service("serial", data, need_resp=True)     # 向串口发送消息
            if ret['status'] != 'ok':
                gw.set_try_data('serial', data)

class GatewayApp(RequestHandler):
    def post(self, cmd):
        try:
            request = self.request.body.decode('utf-8')
            request = json.loads(request)
            body= request["d"]
            if cmd == 'group':
                raise Exception("%s cmd not found" % cmd)
            elif cmd == 'white_list':
                ret = gw.create_whitelist(body['url'], body['md5'])
                if ret:
                    LOG.info("white list create success")
                    resp_status = "ok"
                    resp_data = {"result": "ok"}
                else:
                    raise Exception("white list create failed")
            elif cmd == 'check_code':
                gw.set_auth_key(body['check_code'])
                resp_status = "ok"
                resp_data = {"result":"ok"}
            else:
                raise Exception("%s cmd not found" % cmd)
                
        except Exception as e:
            LOG.error(e.__repr__())
            resp_status = "err",
            resp_data = {"msg":e.__str__()}
        finally:
            upload = uplink.Upload()
            url = r'http://127.0.0.1:7788/mqtt/publish/offlinecache'
            resp = {
                "id": request['id'],
                "from": request['from'],
                "status": resp_status,
                "command": request['command'],
                "d": resp_data
            }
            data = {
                'topic': "dma/cmd/resp",
                'payload':resp
            }
            upload.send(url, data)

