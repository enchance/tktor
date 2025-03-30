from typing import TYPE_CHECKING, Union
from sqlmodel import SQLModel, Relationship
from sqlalchemy.ext.asyncio.session import AsyncSession
from redis_om import NotFoundError, get_redis_connection

from models import modstr
from models.auth_models import ProfileMod, AccountMod, AddressMod, BanMod, RoleMod
from models.common_models import OptionMod
from core import NotFoundException, AppException, logger, utils, ic
from core.config import settings as s


if TYPE_CHECKING:
    from auth import AccountSvc, RoleSvc, AccountCache, UserOptions


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


    @property
    def is_user(self) -> bool:
        return not self.is_moderator and not self.is_admin and not self.is_superadmin


    @property
    def is_moderator(self) -> bool:
        return 'moderator' in self.roles  # noqa


    @property
    def is_admin(self) -> bool:
        return 'admin' in self.roles  # noqa


    @property
    def is_superadmin(self) -> bool:
        return 'superadmin' in self.roles  # noqa


    # TESTME: Untested
    @property
    def permissions(self) -> list[str]:
        """
        Get final list of permissions for the account. This includes stripping any that start with "-" which
        signify that a permission is to be removed not added.
        :return: List of permissions
        """
        red = get_redis_connection()

        # Consolidate perms from roles
        roles = [*self.roles]  # noqa
        if self.is_superadmin:
            roles.extend(['moderator', 'admin'])
        elif self.is_admin:
            roles.extend(['moderator'])

        ll = []
        for role in roles:
            try:
                ll.extend(red.lrange(f'role:{role}', 0, -1))
            except Exception as e:
                logger.error(dict(message=str(e), id=role))
        ll.extend(self.custom_permissions)  # noqa
        return self._reduce_permissions(ll)


    # TESTME: Untested
    @staticmethod
    def _reduce_permissions(permissions: list[str]) -> list[str]:
        """
        Merge permissions by removing any items which start with '-'. For use in collating permissions.
        Duplicates are removed in the process.
        :param permissions: List of permissions
        :return:            Filtered permissions list
        """
        include = set()
        exclude = set()

        for perm in permissions:
            perm = perm.strip()
            if perm.startswith('-'):  # noqa
                exclude.add(perm.strip()[1:])
            else:
                include.add(perm.strip())  # noqa
        resultlist = include - exclude
        return list(resultlist)


    # TESTME: Untested
    @property
    def options(self) -> Union['UserOptions', None]:  # noqa
        """Generate the options for the account."""
        try:
            options_cache = AccountCache.get(self.uid).options  # noqa
            return UserOptions(**options_cache)
        except NotFoundError:
            # TODO: Recache account with Celery
            return
        except Exception as e:
            logger.error(message=str(e), uid=self.uid)  # noqa
            return


    # TESTME: Untested
    @classmethod
    async def create(cls, *, uid: str, email: str, provider: str, avatar: str = '', cache: bool = True,
                     is_banned: bool = False, session: AsyncSession, username: str | None = None,
                     **kwargs) -> 'Account':
        """
        Create a new account and everything needed for it to function.
        :param uid:         Account UID
        :param email:       User email
        :param username:    Username
        :param avatar:      User avatar
        :param provider:    Account provider
        :param is_banned:   Banned or not
        :param cache:       Save to cache
        :param session:     AsyncSession
        :param kwargs:      Kwargs
        :return:            Account
        """
        roles = list(s.defaults.ROLES)
        if _ := kwargs.pop('is_moderator', False):
            roles.extend(['moderator', 'monitor'])
        if _ := kwargs.pop('is_admin', False):
            roles.extend(['admin', 'monitor'])
        if _ := kwargs.pop('is_superadmin', False):
            roles.extend(['superadmin', 'monitor'])

        firstname, lastname, display, kwargs = utils.name_extractor(email, **kwargs)
        account = cls(uid=uid, email=email.lower(), avatar=avatar, roles=roles, display=display,
                      username=username, is_banned=is_banned, is_verified=False)
        session.add(account)
        await session.commit()
        await session.refresh(account)

        # Profile
        meta = dict(provider=[provider])
        profile = ProfileMod(id=account.id, firstname=firstname, lastname=lastname, meta=meta, **kwargs)
        session.add(profile)
        await session.commit()

        if cache and s.USE_CACHE:
            try:
                options = UserOptions(**dict(await AccountSvc.get_options(account.id, session=session)))
                cls.set_cache(account, options=options.model_dump())
            except Exception as e:
                logger.error(dict(message=f'Unable to cache {account.uid}', uid=account.uid, extra=str(e)))

        return account


    # TESTME: Untested
    @staticmethod
    def set_cache(account: 'Account', *, options: dict) -> 'AccountCache':  # noqa
        """
        Cache the account replacing it if exists.
        :param account:     The account to cache
        :param options:     Options dict
        :return:            None
        """
        try:
            valid_keys = list(AccountCache.model_fields.keys())
            d = {k: v for k, v in account.model_dump().items() if k in valid_keys}
            cache = AccountCache(**d, options=options)  # noqa
            cache.pk = account.uid
            cache.save()
            cache.expire(s.ACCOUNT_CACHE_TTL)
            return cache
        except Exception as e:
            logger.error(dict(message=f'Failed to set cache for {account.uid}', uid=account.uid))
            ic(e)


    # TESTME: Untested
    def update_cache(self, data: dict) -> bool:
        """
        Update the account cache based on data.
        :param data:    Keys to update
        :return:
        """
        cache = AccountCache.get(self.uid)
        for key, val in data.items():
            setattr(cache, key, val)
        cache.save()
        return True


class Role(RoleMod, SQLModel, table=True):
    __tablename__ = 'auth_role'


    def __repr__(self):
        return modstr(self, 'name')


    # TESTME: Untested
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


    # TESTME: Untested
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


    # TESTME: Untested
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
