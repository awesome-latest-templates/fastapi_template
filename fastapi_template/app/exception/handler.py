"""Application implementation - custom FastAPI HTTP exception with handler."""
from typing import Any, Optional, Dict

from fastapi import Request
from loguru import logger
from starlette import status

from fastapi_template.app.core import ResponseCode, Response


class HttpException(Exception):
    """Define custom HTTPException class definition.

    This exception combined with exception_handler method allows you to use it
    the same manner as you'd use FastAPI.HTTPException with one difference. You
    have freedom to define returned response body, whereas in
    FastAPI.HTTPException content is returned under "detail" JSON key.

    FastAPI.HTTPException source:
    https://github.com/tiangolo/fastapi/blob/master/fastapi/exceptions.py

    """

    def __init__(
            self,
            code: ResponseCode = ResponseCode.SUCCESS,
            detail: Any = None,
            status_code: int = status.HTTP_200_OK,
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize HTTPException class object instance.

        Args:
            status_code (int): HTTP error status code.
            detail (Any): Response body.
            headers (Optional[Dict[str, Any]]): Additional response headers.

        """
        self.code = code
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __repr__(self):
        """Class custom __repr__ method implementation.

        Returns:
            str: HTTPException string object.

        """
        kwargs = []

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                kwargs.append(f"{key}={value!r}")

        return f"{self.__class__.__name__}({', '.join(kwargs)})"


async def http_exception_handler(request: Request, exception: HttpException):
    """Define custom HTTPException handler.

    In this application custom handler is added in asgi.py while initializing
    FastAPI application. This is needed in order to handle custom HTTException
    globally.

    More details:
    https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers

    Args:
        request (starlette.requests.Request): Request class object instance.
            More details: https://www.starlette.io/requests/
        exception (HttpException): Custom HTTPException class object instance.

    Returns:
        FastAPI.response.JSONResponse class object instance initialized with
            kwargs from custom HTTPException.

    """
    logger.exception("Unhandled exception")
    headers = getattr(exception, "headers", None)
    return Response.fail(code=exception.code,
                         status_code=exception.status_code,
                         message=str(exception.detail) if exception.detail else exception.code.description,
                         headers=headers)
