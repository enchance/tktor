from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Relationship
from sqlalchemy.ext.asyncio.session import AsyncSession
from redis_om import NotFoundError, get_redis_connection

from models import modstr
from models.auth_models import ProfileMod, AccountMod, AddressMod, BanMod, RoleMod
from models.common_models import OptionMod
from core import NotFoundException, AppException, logger
from core.config import settings as s


if TYPE_CHECKING:
    from auth import RoleSvc


class Account(AccountMod, SQLModel, table=True):
    __tablename__ = 'auth_account'
    profile: 'ProfileMod' = Relationship(back_populates='account', sa_relationship_kwargs={'uselist': False})
    options_rel: list['OptionMod'] = Relationship(back_populates='owner')
    addresses: list['AddressMod'] = Relationship(back_populates='account')
    bans: list['BanMod'] = Relationship(
        back_populates='account', sa_relationship_kwargs={'foreign_keys': '[BanMod.recipient_id]'})
    ban_owners: list['BanMod'] = Relationship(
        back_populates='banner', sa_relationship_kwargs={'foreign_keys': '[BanMod.owner_id]'})


    def __repr__(self):
        return modstr(self, 'email')


class Role(RoleMod, SQLModel, table=True):
    __tablename__ = 'auth_role'


    def __repr__(self):
        return modstr(self, 'name')


    @classmethod
    async def get(cls, name: str, *, use_db: bool = False, session: AsyncSession) -> set[str]:
        """
        Return a role and its permissions. Does not return an object.
        :param name:        Role name
        :param use_db:      Get from db directly skipping cache
        :param session:     AsyncSession
        :return:            Account
        """
        if use_db:
            try:
                if role := await RoleSvc.get_by_name(name, session=session):
                    return role.permissions  # noqa
                raise NotFoundException('ROLE_NOT_FOUND')
            except NotFoundException:
                raise
            except Exception as e:
                logger.error(dict(message=str(e), id=name))
                raise AppException('ROLE_RETRIEVAL_FAILED')

        try:
            # From here it checks the cache first
            if cache := cls.get_cache(name):
                # ic('WITH_CACHE')
                return cache
            # ic('NO_CACHE')
            raise NotFoundError('CACHE_NOT_FOUND')
        except NotFoundError:
            if role := await RoleSvc.get_by_name(name, session=session):
                if s.USE_CACHE:
                    cls.set_cache(name, role.permissions)  # noqa
                return role.permissions  # noqa
            raise NotFoundException('ROLE_NOT_FOUND')
        except Exception as e:
            logger.error(dict(message=str(e), id=name))
            raise AppException('ROLE_RETRIEVAL_FAILED')


    @staticmethod
    def get_cache(name: str) -> set[str] | None:  # noqa
        """
        Get the cache for this role or recache it if it doesn't exist.
        :return:    AccountCache or None
        """
        red = get_redis_connection()
        try:
            cache_key = f'role:{name}'
            return set(red.lrange(cache_key, 0, -1))
        except NotFoundError:
            return
        except Exception as e:
            logger.error(dict(message=str(e), id=name))
            return


    @staticmethod
    def set_cache(name: str, permissions: set[str], replace: bool = True) -> bool:  # noqa
        """
        Cache the role.
        :param name:        Role name
        :param permissions: Role permissios
        :return:            None
        """
        red = get_redis_connection()

        try:
            cache_key = f'role:{name}'
            pipe = red.pipeline()
            if replace:
                pipe.delete(cache_key)
            pipe.rpush(cache_key, *permissions)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(dict(message=f'Failed to set cache for role {name}', uid=name))
            # ic(e)
            return False
