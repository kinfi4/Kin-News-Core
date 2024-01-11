class KinNewsCoreException(Exception):
    pass


class InvalidChannelURLError(KinNewsCoreException):
    pass


class AccessForbidden(KinNewsCoreException):
    pass


class ServiceProxyError(KinNewsCoreException):
    pass


class ServiceProxyNotFoundError(ServiceProxyError):
    pass


class ServiceProxyDuplicateError(ServiceProxyError):
    pass


class ServiceUnavailable(KinNewsCoreException):
    pass


class TelegramIsUnavailable(ServiceUnavailable):
    seconds_to_wait: int

    def __init__(self, msg: str, seconds: int):
        super().__init__(msg)
        self.seconds_to_wait = seconds


class RedditIsUnavailable(ServiceUnavailable):
    def __init__(self, msg: str):
        super().__init__(msg)


class AuthenticationFailedError(KinNewsCoreException):
    pass
