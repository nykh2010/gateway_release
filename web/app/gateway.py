from tornado.web import RequestHandler
from auth import auth
from config import Config
import os
from hashlib import sha256

class GatewayHandler(RequestHandler):
    @auth
    def get(self,method):
        if method == 'restart':
            self.render("restart.html")
        elif method == 'id':
            gateway = {}
            with open('/etc/gateway/sn', 'r') as fp:
                sn = fp.read()
            gateway['sn'] = sn
            self.render("gateway_setup.html", gateway=gateway)
        elif method == 'firmware':
            self.render("upgrade.html")
        elif method == 'time':
            self.render("settime.html")
        elif method == 'restore':
            self.render("restore.html")
        else:
            self.set_status(404, "page not found")
    
    def post(self,method,*args):
        ret = {}
        if method == 'restart':
            os.system("reboot")
            ret['status'] = 'success'
        elif method == 'update':
            if args[0] == 'id':
                # 修改网关地址
                try:
                    # gateway = Config("gateway")
                    gateway_id = self.get_argument('id')
                    with open('/etc/gateway/sn', 'w') as fp:
                        fp.write(gateway_id)
                    # gateway.set_item('sn', gateway_id)
                    # gateway.save()
                    status = os.system('/home/root/kill_process msghub')
                    ret['status'] = 'success'
                    if status != 0:
                        raise Exception("参数错误")                          
                except Exception as e:
                    ret['status'] = 'failed'
                    ret['err_msg'] = e.__str__()
            elif args[0] == 'time':
                # 修改系统时间
                year = self.get_argument('year')
                month = self.get_argument('month')
                day = self.get_argument('day')
                hour = self.get_argument('hour')
                minute = self.get_argument('minute')
                second = self.get_argument('second')
                cmd = 'date -s "{0}-{1}-{2} {3}:{4}:{5}"'.format(year, month, day, hour, minute, second)
                status = os.system(cmd)
                ret['status'] = 'success'
                if status != 0:
                    ret['status'] = 'failed'
                    ret['err_msg'] = 'set time failed'                
        elif method == 'upgrade':
            content = self.request.files['put_file'][0]['body']
            file_name = self.request.files['put_file'][0]['filename']
            file_hash = self.get_argument('sha256')
            hash_obj = sha256()
            hash_obj.update(content)
            hash_result = hash_obj.hexdigest()
            if file_hash != hash_result:
                ret['status'] = 'failed'
                ret['err_msg'] = 'file check failed'
                self.write(ret)
                return
            
            if "zip" in file_name or "tar.gz" in file_name:
                with open('/media/%s' % file_name, 'wb') as fp:
                    fp.write(content)
                status = self.install(file_name)
                if status != 0:
                    ret['status'] = 'failed'
                    ret['err_msg'] = 'install failed'
                else:
                    ret['status'] = 'success'
        elif method == 'restore':
            if not (os.path.exists('/media/bin') and os.path.exists('/media/gateway')):
                ret['status'] = 'failed'                    # 未找到备份文件
                ret['err_msg'] = 'can not found backup file'
                self.write(ret)
                return
            apps = os.listdir('/usr/local/bin')
            for app in apps:
                # 杀死所有app
                os.system('/home/root/kill_process %s' % app)
                os.system("rm /usr/local/bin/%s -rf" % app)
            os.system("rm /etc/gateway -rf")
            os.system("cp /media/bin /usr/local -rf")       # 恢复应用程序
            os.system("cp /media/gateway /etc -rf")         # 恢复配置文件
            os.system("reboot &")                           # 重启
            ret['status'] = 'success' 
        elif method == 'backup':
            os.system('cp /usr/local/bin /media -rf')
            os.system('cp /etc/gateway /media -rf')
            ret['status'] = 'success'
        self.write(ret)

    def install(self, file_name):
        os.system("tar -xvf /media/%s -C /media/install" % file_name)
        if not os.access('/media/install/INSTALL', os.X_OK):
            os.chmod('/media/install/INSTALL', os.X_OK)
        ret = os.system("/media/install/INSTALL")
        os.system("rm /media/%s /media/install -rf" % file_name)
        return ret
            

                
        