
class EpdException(Exception):
    def __init__(self, code=200, message="success"):
        self.code = code
        self.message = message
