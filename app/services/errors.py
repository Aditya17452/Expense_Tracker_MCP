class ServiceError(Exception):
    """Base class for errors raised by the service layer."""


class NotFoundError(ServiceError):
    pass


class PermissionDeniedError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class AuthenticationError(ServiceError):
    pass
