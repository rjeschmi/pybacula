
class PyBaculaException(Exception):
    """Base class for exceptions in PyBacula"""
    pass


class FileNotFound(PyBaculaException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
