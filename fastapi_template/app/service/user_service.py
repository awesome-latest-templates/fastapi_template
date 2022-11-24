import datetime
from typing import Optional

from sqlalchemy.orm import Session

from fastapi_template.app import crud, model
from fastapi_template.app.core import ResponseCode
from fastapi_template.app.core.auth.security import verify_password, create_access_token
from fastapi_template.app.entity.auth_entity import TokenPayload
from fastapi_template.app.entity.user_entity import UserLoginRequest, UserResponse
from fastapi_template.app.exception import HttpException


class UserService:

    async def create_token_async(self, login_data: UserLoginRequest) -> UserResponse:
        response = UserResponse()
        username = login_data.username
        password = login_data.password
        try:
            if not (username and password):
                raise HttpException(ResponseCode.BAD_REQUEST, "username or password is empty")
            result_data: Optional[model.User] = await crud.user.query_by_username(username=username)
            if not result_data:
                raise HttpException(ResponseCode.NOT_FOUND, "not found associated user")
            store_password = result_data.password
            valid_password = verify_password(password, store_password)
            if not valid_password:
                raise HttpException(ResponseCode.BAD_REQUEST, "password is incorrect")
            is_active = result_data.is_active == 1
            if not is_active:
                raise HttpException(ResponseCode.FORBIDDEN, "user is deactivate")
            response.id = result_data.id
            response.user_name = result_data.user_name
            response.nick_name = result_data.nick_name
            response.last_login_time = result_data.last_login_time
            response.avatar = result_data.avatar
            # create the token
            token_data = TokenPayload()
            token_data.id = response.id
            token = create_access_token(token_data, datetime.timedelta(days=1))
            response.token = token

            return response
        except Exception as e:
            raise HttpException(ResponseCode.HTTP_ERROR, "login unexpected error")

    def get_user_detail(self, user_id: str, session: Session) -> model.User:
        resp = session.query(model.User).filter(model.User.Id == user_id, model.User.IsActive == 1).first()
        return resp


user = UserService()
