from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def error_payload(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message, exc.details),
    )


def serializable_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned_errors: list[dict[str, Any]] = []
    for error in errors:
        cleaned_error = dict(error)
        if isinstance(cleaned_error.get("ctx"), dict):
            cleaned_error["ctx"] = {key: str(value) for key, value in cleaned_error["ctx"].items()}
        cleaned_errors.append(cleaned_error)
    return cleaned_errors


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_payload(
            "VALIDATION_ERROR",
            "Request validation failed.",
            {"errors": serializable_validation_errors(exc.errors())},
        ),
    )
