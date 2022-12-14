import decimal
import typing
from datetime import datetime

import orjson
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from orjson.orjson import OPT_UTC_Z
from pydantic import BaseModel
from starlette import status
from starlette.background import BackgroundTask

from fastapi_template.app.exception.status import ResponseCode


class Response(ORJSONResponse):

    def __init__(self,
                 content: typing.Any,
                 status_code: int = 200,
                 headers: typing.Optional[dict] = None,
                 media_type: typing.Optional[str] = None,
                 background: typing.Optional[BackgroundTask] = None,
                 ):
        super(Response, self).__init__(content, status_code, headers, media_type, background)

    def render(self, content: typing.Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(content,
                            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY | OPT_UTC_Z,
                            default=self.default_encode)

    @staticmethod
    def default_encode(obj: typing.Any):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return jsonable_encoder(obj, exclude_unset=True, exclude_none=True)

    @staticmethod
    def ok(data: typing.Any = None,
           message: str = "success",
           status_code: int = status.HTTP_200_OK,
           headers: typing.Optional[dict] = None) -> "Response":
        resp_data = Response._build_response(data=data, message=message)
        resp = Response(content=resp_data, status_code=status_code, headers=headers)
        return resp

    @staticmethod
    def fail(code: ResponseCode,
             message: str = "failed",
             status_code: int = status.HTTP_200_OK,
             headers: typing.Optional[dict] = None) -> "Response":
        resp_data = Response._build_response(code=code, message=message, success=False)
        resp = Response(content=resp_data, status_code=status_code, headers=headers)
        return resp

    @staticmethod
    def _build_response(
            code: ResponseCode = ResponseCode.SUCCESS,
            message: str = "",
            success: bool = True,
            data: typing.Any = None):
        if isinstance(data, BaseModel):
            result: BaseModel = data
            data = result.dict()
        resp_data: dict = {
            "code": code.code,
            "message": message,
            "success": success,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return resp_data
