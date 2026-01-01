from fastapi import status


class AppException(Exception):
    """Base app exception with message + status code."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationException(AppException):
    """Raised for business rule validation errors."""
    def __init__(self, message: str = "Invalid input data"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)
