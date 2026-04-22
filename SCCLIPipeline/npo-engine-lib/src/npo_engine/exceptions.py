

class EngineException(Exception):
    message: str
    ex: Exception

    def __init__(self, msg: str = None, ex: Exception = None):
        self.message = msg
        self.ex = ex
        super().__init__(msg)
