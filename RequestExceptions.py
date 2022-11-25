class Error(Exception):
    """Base class for exceptions"""
    pass

class BadRequest(Error):
    """Raised because status code 400"""
    pass

class Unauthorized(Error):
    """Raised because status code 401"""
    pass

class Forbidden(Error):
    """Raised because status code 403"""
    pass

class DataNotFound(Error):
    """Raised because status code 404"""
    pass

class MethodNotAllowed(Error):
    """Raised because status code 405"""
    pass

class UnsupportedMediaType(Error):
    """Raised because status code 415"""
    pass

class RateLimitExceeded(Error):
    """Raised because status code 429"""
    pass

class InternalServerError(Error):
    """Raised because status code 500"""
    pass

class BadGateway(Error):
    """Raised because status code 502"""
    pass

class ServiceUnavailable(Error):
    """Raised because status code 503"""
    pass

class GatewayTimeout(Error):
    """Raised because status code 504"""
    pass