from fastapi.exceptions import HTTPException


class AppException(HTTPException):
    def __init__(self, detail: str | None = None, status_code: int | None = None):
        status_code = status_code or 400
        detail = detail or 'APP_ERROR'
        super().__init__(status_code=status_code, detail=detail)


class InvalidToken(AppException):
    def __init__(self, detail: str | None = None, status_code: int | None = None):
        status_code = status_code or 403
        detail = detail or 'INVALID_TOKEN'
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    def __init__(self, detail: str | None = None, status_code: int | None = None):
        status_code = status_code or 404
        detail = detail or 'NOT_FOUND'
        super().__init__(status_code=status_code, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str | None = None, status_code: int | None = None):
        status_code = status_code or 403
        detail = detail or "YOU_HAVE_NO_POWER_HERE"
        super().__init__(status_code=status_code, detail=detail)
