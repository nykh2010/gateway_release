from tornado.web import RequestHandler
from auth import auth

class StatusHandler(RequestHandler):
    @auth
    def get(self):
        self.render("info.html")