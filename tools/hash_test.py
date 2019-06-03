import hashlib

def get_whitelist():
    try:
        with open('/home/xulingfeng/whitelist', 'rb') as whitelistfile:
            content = whitelistfile.read()
            __whitelist = set(content.decode('utf-8').split('\n'))
            hash_obj = hashlib.md5()
            hash_obj.update(content)
            return str(hash_obj.hexdigest())
    except Exception as e:
        print("get white list failed: %s" % e.__str__())


rest = get_whitelist()
print(rest)