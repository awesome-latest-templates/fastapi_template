from typing import Optional

from fastapi_cache.decorator import cache

from fastapi_template.app import crud
from fastapi_template.app.core.log import logger
from fastapi_template.app.entity.user_entity import UserDetail


class UserService:

    @cache()
    async def get_user_detail(self, user_id: int) -> Optional[UserDetail]:
        # get user roles
        user_data = await crud.user.get_by_id(item_id=user_id)
        if not user_data:
            logger.warning(f'not found the user with user_id: {user_id}')
            return None
        user_role_data = await crud.user_role.query_by_user_id(user_id=user_id)
        if not user_role_data:
            logger.warning(f'not found the user role data with user_id: {user_id}')
            return None
        role_ids = list(map(lambda d: d.role_id, user_role_data))
        role_datas = await crud.role.get_by_ids(list_ids=role_ids)
        role_names = list(map(lambda d: d.name, role_datas))
        user_detail = UserDetail(**user_data.dict())
        user_detail.role = role_names
        return user_detail


user = UserService()
