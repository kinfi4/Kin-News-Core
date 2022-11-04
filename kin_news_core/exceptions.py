class KinNewsCoreException(Exception):
    pass


class InvalidChannelURLError(KinNewsCoreException):
    pass


class AccessForbidden(KinNewsCoreException):
    pass
