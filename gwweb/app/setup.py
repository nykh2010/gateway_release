from tornado.web import RequestHandler
from auth import auth


class SetupHandler(RequestHandler):
    @auth
    def get(self, *args, **kwargs):
        self.render('setup.html')
    
    def post(self, method):
        if method == 'wifi':
            pass
        elif method == 'server':
            pass
        elif method == 'restart':
            pass
        self.write("['SUCCESS']")
    
    def options(self, method):
        pass
