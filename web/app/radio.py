from tornado.web import RequestHandler
from auth import auth
from config import Config
from connect_service import send_to_service
from tornado.log import app_log as LOG

class RadioHandler(RequestHandler):
    '''射频参数配置'''
    @auth
    def get(self):
        radio1 = Config("radio1")
        radio2 = Config("radio2")
        if radio1.enable:
            radio_1_param = self.render_string("radio1_param.html", radio=radio1)
        else:
            radio_1_param = '''
                <p>射频模块1无效</p>
            '''
        if radio2.enable:
            radio_2_param = self.render_string("radio2_param.html", radio=radio2)
        else:
            radio_2_param = '''
                <p>射频模块2无效</p>
            '''
        self.render("radiosetup.html", radio_1=radio_1_param, radio_2=radio_2_param)

    def post(self, cmd):
        ret = {}
        try:
            if cmd == "update":
                radio_number = self.get_argument("radio_number")
                if (radio_number == '1'):
                    # print("radio1")
                    radio = Config("radio1")
                    wakeup = self.get_argument("wakeup")
                    trycount = self.get_argument("trycount")
                    wait = self.get_argument("wait")
                    transmode = self.get_argument("transmode")
                    radio.set_item("wakeup", wakeup)
                    radio.set_item("trycount",trycount)
                    radio.set_item("wait", wait)
                    radio.set_item("transmode", transmode)
                    radio.save()
                    data = {
                        "cmd":"update",
                        "radio_number":"1"
                    }
                    resp = send_to_service('serial', data=data)
                    if resp['status'] != "ok":
                        raise Exception(resp['msg'])
                else:
                    radio = Config("radio2")
                    data = {
                        "cmd":"update",
                        "radio_number":"2"
                    }
                    resp = send_to_service('serial', data=data)
                    if resp['status'] != "ok":
                        raise Exception
                ret['status'] = 'success'
            elif cmd == "restart":
                radio_number = self.get_argument("radio_number")
                data = {
                    "cmd":"restart",
                    "radio_number":radio_number
                }
                resp = send_to_service('serial', data=data)
                if resp['status'] != "ok":
                    raise Exception(resp['msg'])
        except Exception as e:
            ret['status'] = 'failed'
            ret['err_msg'] = e.__repr__()
            LOG.error(e.__str__())
        self.write(ret)