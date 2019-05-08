import os
# import json
# from threading import Thread
# import time
# from gateway import gateway
from config import Config
# from uplink import upload

class EpdTask(Config):
    __execute_list = set()
    def __init__(self, path):
        super().__init__('epdtask', path=path)
        # self.check_task_file()
        self.update_execute_list()
    
    # def check_task_file(self):
    #     options = ['execute_url', 'data_url']
    #     flag = False
    #     if not self.has_section('epdtask'):
    #         flag = False
    #     else:
    #         for option_name in options:
    #             if not self.has_option(option_name):
    #                 self.set('epdtask', option_name)

    def update_execute_list(self):
        try:
            with open(self.execute_url, 'r') as f:
                content = f.read()
                self.__execute_list = set(content.split('\n'))
        except:
            pass

    def is_in_executelist(self, device_id):
        return device_id in self.__execute_list

# epd = EpdTask()
# print(dir(epd))

# class Task:
#     __taskList = []
#     try:
#         with open('task', 'r') as taskFile:
#             tasks = json.load(taskFile)
#             for task in tasks:
#                 __taskList.append(task)
#     except:
#         with open('task', 'w') as taskFile:
#             json.dump(__taskList, taskFile)

#     def __init__(self):
#         self.__taskId = ''
#         self.__taskStatus = 'none'
#         self.__taskTime = ''
#         self.__taskTimeSn = None
#         self.__taskImageId = ''
#         self.__taskImageUrl = ''
#         self.__List = []

#     def check_status(self, task_id=None, device_id=None, image_id=None):
#         if task_id is None and device_id is None:
#             return False
        
#         # 查询任务状态
#         if device_id is None:
#             # 来自服务端的任务创建请求
#             for task in self.__taskList:
#                 if task['task_id'] == task_id:
#                     if task['task_status'] not in ['none', 'finish', 'sleep']:
#                         return False
#                     else:
#                         return True
#             return True
#         else:
#             # 终端查询
#             for task in self.__taskList:
#                 if device_id not in task['list']:
#                     pass
#                 elif image_id != task['image_id']:
#                     pass
#                 elif task['status'] not in ['finish','sleep','ready']:
#                     pass
#                 else:
#                     return task
                
#             return False
        
#     def get_status(self, task_id):
#         for task in self.__taskList:
#             if task_id == task['task_id']:
#                 return task['status']

#     def create_task(self, body):
#         taskContent = body
#         # 参数完整性检查
#         if "task_id" and "image_id" and "image_url" and "time" and "list" not in taskContent.keys():
#             return False, "任务参数不完整"
#         self.__taskId = taskContent['task_id']
#         self.__taskImageId = taskContent['image_id']
#         self.__taskImageUrl = taskContent['image_url']
#         self.__List = taskContent['list']
#         self.__taskStatus = 'sleep'
#         self.__taskTime = taskContent['time']
#         self.write_task()
#         return True, "任务创建完成"

#     def write_task(self):
#         data = {}
#         data['task_id'] = self.__taskId
#         data['image_id'] = self.__taskImageId
#         data['image_url'] = self.__taskImageUrl
#         data['list'] = self.__List
#         data['status'] = self.__taskStatus
#         data['time'] = self.__taskTime
#         data['time_sn'] = self.__taskTimeSn
#         self.__taskList.append(data)
#         with open('task', 'w') as taskFile:
#             json.dump(self.__taskList, taskFile, indent=4)

#     def cancel_task(self, task_id):
#         if task_id != self.__taskId:
#             return False, "任务不存在"
#         else:
#             self.__taskStatus = 'none'
#             return True, "取消成功"
    
#     def confirm_task(self, body):
#         taskContent = body
#         if 'task_id' and 'time' not in taskContent.keys():
#             return False, "任务参数不完整"
#         if taskContent['task_id'] != self.__taskId:
#             return False, "任务不存在"
#         self.__taskTime = taskContent['time']
#         self.__taskStatus = "ready"
#         self.write_task()
#         return True

#     def get_time(self, task_id):
#         # 返回倒计时时间
#         for task in self.__taskList:
#             if task_id == task['task_id']:
#                 if task['status'] == 'ready' and task['time_sn'] is not None:
#                     return gateway.get_starttime(task['time'], task['time_sn'])
#                 elif task['status'] == 'sleep':
#                     sn = gateway.get_worktime(task_id)
#                     task['status'] = 'ready'
#                     task['time_sn'] = sn
#                     with open('task', 'w') as taskFile:
#                         json.dump(self.__taskList, taskFile, indent=4)
#                     return gateway.get_starttime(task['time'], sn)
#                 else:
#                     return None
#         return None

#     def send_cache(self, payload):
#         print("send cache", payload)
#         from uplink import upload
#         upload.send(payload,cache=True)

#     def task_service(self, *args, **kwargs):
#         print('task service start...')


#     def start_service(self):
#         # 任务处理服务
#         # 1、向上发送任务状态缓存
#         # 2、接受任务处理
#         # content = json.dumps(self.__taskList)
#         content = {}
#         content['name'] = 'epd_service'
#         content['task'] = self.__taskList.copy()
#         self.send_cache(content)        # 上报任务状态
#         # self.__taskThread = Thread(target=self.task_service, name='task')
#         # self.__taskThread.start()


# task = Task()