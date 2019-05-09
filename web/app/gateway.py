from tornado.web import RequestHandler
from auth import auth
from config import Config
import os
from hashlib import sha256

class GatewayHandler(RequestHandler):
    @auth
    def get(self,method):
        gateway = Config("gateway")
        firmware = Config("firmware")
        if method == 'restart':
            self.render("restart.html")
        elif method == 'id':
            self.render("gateway_setup.html", gateway=gateway)
        elif method == 'firmware':
            self.render("upgrade.html", firmware=firmware)
        elif method == 'time':
            self.render("settime.html", firmware=firmware)
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
                    gateway = Config("gateway")
                    gateway_id = self.get_argument('id')
                    gateway_mac = self.get_argument('mac')
                    gateway_key = self.get_argument('key')

                    gateway.set_item('id', gateway_id)
                    gateway.set_item('mac', gateway_mac)
                    gateway.set_item('key', gateway_key)  
                    gateway.save()
                    ret['status'] = 'success'
                except Exception as e:
                    ret['status'] = 'failed'
                    ret['err_msg'] = e.__repr__()
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
                service_conf = Config("service")
                firmware_path = os.path.join(service_conf.path, file_name)
                with open(firmware_path, 'wb') as f:
                    f.write(content)
                ret['status'] = 'success'
            else:
                ret['status'] = 'failed'
                ret['err_msg'] = 'format error'  
                os.system('rm %s' % firmware_path)
        elif method == 'restore':
            os.system('cp /var/default/*.ini /etc/config')
            os.system('reboot &')
            ret['status'] = 'success' 
                
        self.write(ret)