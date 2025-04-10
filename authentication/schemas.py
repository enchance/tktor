from typing import Union, TYPE_CHECKING
from datetime import datetime
from pydantic import model_validator, BaseModel, field_validator, Field as PydanticField
from redis_om import JsonModel, Field

from core import ic, logger
from core.config import settings as s
from authentication import Auth as auth_


# from core.schemas import SystemOptionsSchema
# from account import models


class RoleCache(JsonModel):
    name: str = Field(index=True)
    permissions: list[str]


class BaseAccount(BaseModel):
    uid: str
    email: str
    display: str
    username: str
    avatar: str
    custom_permissions: list[str]


class AccountCreate(BaseModel):
    uid: str
    email: str
    email_verified: bool
    picture: str
    send_verification: bool = PydanticField(default=True)


class AccountCache(BaseAccount, JsonModel):
    id: int = Field(index=True)
    roles: list[str]
    options: dict
    is_banned: bool
    is_verified: bool


    @model_validator(mode='before')
    def _validate_model_fields(cls, val):  # noqa
        if val['username'] is None:
            val['username'] = ''
        if val['is_banned'] is None:
            val['is_banned'] = False
        # if isinstance(val['banned_at'], datetime):
        #     val['banned_at'] = val['banned_at'].isoformat()

        return val


    def to_account(self) -> Union['Account', None]:  # noqa
        try:
            d = self.model_dump()
            del d['options']
            d['username'] = d['username'] or None

            if not d['is_banned']:
                d['is_banned'] = False
            # else:
            #     d['banned_at'] = datetime.fromisoformat(d['banned_at'])

            account = auth_.Account(**d, banned_by_id=None)  # noqa
            account.is_cache = True
            return account
        except Exception as e:
            logger.error(dict(message=str(e)))
            return None


class FetchAccount(BaseAccount):
    id: int
    is_banned: bool
    is_verified: bool
    token: str = PydanticField(default='')


class UserOptions(BaseModel):
    date_format: str
    time_format: str
    timezone: str
    items_per_page: int
    comment_publish_delay: int
    comments_per_page: int
    comment_order: str
    # comments_blacklist: set[str]
    max_upload_mb: int
    pointer_all_orders: int
    pointer_all_trades: int


    # @field_validator('default_role', mode='before')
    # def transform_default_role(cls, val):
    #     if isinstance(val, str):
    #         return map(lambda x: x.strip(), str(val).split(','))
    #     return val

    # @field_validator('comments_blacklist', mode='before')
    # def transform_comments_blacklist(cls, val):
    #     if isinstance(val, str):
    #         if setdata := map(lambda x: x.strip(), str(val).split(',')):
    #             cleaned = filter(None, setdata)
    #             return cleaned
    #     return val


# TESTME: Untested
class SystemOptionsCache(JsonModel):
    site_name: str
    site_description: str
    site_icon: str
    site_url: str
    admin_email: str
    home_path: str
    users_can_register: bool
    comment_status: str
    comment_anonymous: bool
    comment_threads: bool
    comment_depth: int
    show_avatars: bool
    avatar_default_url: str


# TESTME: Untested
class ShortcodeCredentials(BaseModel):
    email: str
    password: str

# class FetchFullAccount(BaseModel):
#     id: int
#     uid: str
#     email: str
#     display: str
#     avatar: str
#
#
# class FetchFullAccount(BaseAccount):
#     provider: list[str] = PydanticField(exclude=True)
#     custom_permissions: list[str] = PydanticField(exclude=True)


# class CreateAccount(BaseModel):
#     pass
