from config import Config
import os

os.chdir(os.path.dirname(__file__))
webserver = Config("web")
try:
    os.execv("webserver.py", ("webserver.py --host=%s --port=%s" % (webserver.host, webserver.port),))
except:
    os.execv("webserver.py", ("webserver.py",))