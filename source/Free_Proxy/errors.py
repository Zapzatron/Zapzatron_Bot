"""FreeProxy exceptions module"""


class FreeProxyZapzatronException(Exception):
    """Exception class with message as a required parameter"""
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)
