class KinNewsCoreException(Exception):
    pass


class InvalidChannelURLError(KinNewsCoreException):
    pass


class AccessForbidden(KinNewsCoreException):
    pass


class ServiceProxyError(KinNewsCoreException):
    pass


class TelegramIsUnavailable(KinNewsCoreException):
    seconds_to_wait: int

    def __init__(self, msg: str, seconds: int):
        super().__init__(msg)
        self.seconds_to_wait = seconds
