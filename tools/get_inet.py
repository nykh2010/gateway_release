import os
import re

# with os.popen('ifconfig lo | grep inet\ addr') as fp:
#     res = fp.readlines()
# for r in res:
#     conf = r.strip()
# p = re.match(r'inet addr:(.*\d+).*Mask:(.*)', conf)
# print(p.groups())

def set_dhcp_mode():
    print('set_dhcp_mode')

def set_static_mode(inet, netmask):
    print(inet)
    print(netmask)

def set_mode(mode, *args):
    if mode == 'dhcp':
        set_dhcp_mode(*args)
    elif mode == 'static':
        set_static_mode(*args)

set_mode('static', '127.0.0.1', '255.255.255.0')