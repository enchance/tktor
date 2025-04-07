from typing import TYPE_CHECKING, Union
from sqlmodel import SQLModel, Relationship
from sqlalchemy.ext.asyncio.session import AsyncSession
from redis_om import NotFoundError, get_redis_connection

from models import modstr
from models.auth_models import Profile, AccountMod, Address, Ban, RoleMod
from models.common_models import Option, Taxonomy
from core import NotFoundException, AppException, logger, utils, ic, OptionsSvc, ForbiddenException
from core.config import settings as s
from authentication import enums, schemas, services as svc
from dev.data import SEED_USER_OPTIONS
from exchange import Order, Trade, Wallet, Exchange


if TYPE_CHECKING:
    from . import RoleSvc


class Account(AccountMod, SQLModel, table=True):
    __tablename__ = 'auth_account'
    profile: 'Profile' = Relationship(back_populates='account', sa_relationship_kwargs={'uselist': False},
                                      cascade_delete=True)
    taxonomies: list['Taxonomy'] = Relationship(back_populates='account')
    options_rel: list['Option'] = Relationship(back_populates='account', cascade_delete=True)
    addresses: list['Address'] = Relationship(back_populates='account', cascade_delete=True)
    bans_received: list['Ban'] = Relationship(
        back_populates='account', sa_relationship_kwargs={'foreign_keys': '[Ban.account_id]'}, cascade_delete=True)
    bans_implemented: list['Ban'] = Relationship(
        back_populates='implementor', sa_relationship_kwargs={'foreign_keys': '[Ban.implementor_id]'}, cascade_delete=True)

    orders: list['Order'] = Relationship(back_populates='account', cascade_delete=True)
    trades: list['Trade'] = Relationship(back_populates='account', cascade_delete=True)
    wallets: list['Wallet'] = Relationship(back_populates='account', cascade_delete=True)


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
                cache = schemas.RoleCache.get(role)
                ll.extend(cache.permissions)
                # ll.extend(red.lrange(f'role:{role}', 0, -1))
            except Exception as e:
                logger.error(dict(message=str(e), id=role))
        ll.extend(self.custom_permissions)  # noqa
        return self._reduce_permissions(ll)


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


    @property
    def options(self) -> Union['UserOptions', None]:  # noqa
        """Generate the options for the account."""
        try:
            options_cache = schemas.AccountCache.get(self.uid).options  # noqa
            return schemas.UserOptions(**options_cache)
        except NotFoundError:
            # TODO: Recache account with Celery
            return
        except Exception as e:
            logger.error(message=str(e), uid=self.uid)  # noqa
            return


    @classmethod
    async def get(cls, uid: str, *, use_db: bool = False,
                  session: AsyncSession) -> Union['Account', None]:
        """
        Return an instance of an account. Checks the cache before querying the db.
        If cache is empty then it hits the db and resaves it to cache for future queries.
        :param uid:             Account.uid
        :param use_db:          Get from db directly skipping cache
        :param session:         AsyncSession
        :return:                Account
        """


        async def _recache_account(to_cache: Account):
            d = await svc.AccountSvc.get_options(to_cache.id, session=session)
            options = schemas.UserOptions(**d)
            cls.set_cache(to_cache, options=options.model_dump())


        async def _fetch_account():
            if account := await svc.AccountSvc.get_by_uid(uid, session=session):
                if s.USE_CACHE:
                    await _recache_account(account)
                account.is_cache = False
                return account
            raise NotFoundException('ACCOUNT_NOT_FOUND')


        if use_db:
            try:
                return await _fetch_account()
            except NotFoundException:
                raise
            except Exception as e:
                logger.error(dict(message=str(e), id=uid, ))
                raise AppException('ACCOUNT_RETRIEVAL_FAILED')

        try:
            # From here it checks the cache first
            if cache := cls.get_cache(uid):
                if account := cache.to_account():  # noqa
                    account.is_cache = True
                    return account
                raise AppException('CACHE_TO_ACCOUNT_FAILED')
            raise NotFoundError('CACHE_NOT_FOUND')
        except NotFoundError:
            return await _fetch_account()
        except Exception as e:
            logger.error(dict(message=str(e), id=uid, ))
            raise AppException('ACCOUNT_RETRIEVAL_FAILED')


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

        kw = kwargs.copy()
        meta = dict(provider=[provider])
        for i in kw.keys():
            if i not in {*Account.model_fields.keys(), *Profile.model_fields.keys()}:
                meta[i] = kwargs.pop(i)

        account = cls(
            uid=uid, email=email.lower(), avatar=avatar, roles=roles, display=display, username=username,
            is_banned=is_banned, is_verified=False,
            profile=Profile(firstname=firstname, lastname=lastname, meta=meta, **kwargs),
            # addresses=[
            #     AddressMod(),
            #     AddressMod(),
            # ],
            options_rel=[Option(**i, type=2) for i in SEED_USER_OPTIONS]
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)

        if cache and s.USE_CACHE:
            try:
                options = schemas.UserOptions(**dict(await svc.AccountSvc.get_options(account.id, session=session)))
                cls.set_cache(account, options=options.model_dump())
            except Exception as e:
                logger.error(dict(message=f'Unable to cache {account.uid}', uid=account.uid, extra=str(e)))

        return account


    @staticmethod
    def get_cache(uid: str) -> Union['AccountCache', None]:  # noqa
        """
        Get the cache for this account or recache it if it doesn't exist.
        :return:    AccountCache or None
        """
        try:
            return schemas.AccountCache.get(uid)
        except NotFoundError:
            return
        except Exception as e:
            logger.error(dict(message=str(e), id=uid))
            return


    @staticmethod
    def set_cache(account: 'Account', *, options: dict) -> schemas.AccountCache:  # noqa
        """
        Cache the account replacing it if exists.
        :param account:     The account to cache
        :param options:     Options dict
        :return:            None
        """
        try:
            valid_keys = list(schemas.AccountCache.model_fields.keys())
            d = {k: v for k, v in account.model_dump().items() if k in valid_keys}
            cache = schemas.AccountCache(**d, options=options)  # noqa
            cache.pk = account.uid
            cache.save()
            cache.expire(s.ACCOUNT_CACHE_TTL)
            return cache
        except Exception as e:
            logger.error(dict(message=f'Failed to set cache for {account.uid}', uid=account.uid))
            ic(e)


    def update_cache(self, data: dict) -> bool:
        """
        Update the account cache based on data.
        :param data:    Keys to update
        :return:
        """
        cache = schemas.AccountCache.get(self.uid)
        for key, val in data.items():
            setattr(cache, key, val)
        cache.save()
        return True


    async def update_options(self, data: dict, *, session: AsyncSession) -> bool:
        """
        Update the account options based on data.
        :param data:        Options to update
        :param session:     AsyncSession
        :return:            bool
        """
        if _ := await OptionsSvc.update(self.id, data, session=session):
            options = self.options
            for key, val in data.items():
                setattr(options, key, val)
            self.update_cache({'options': options.model_dump()})
            return True


    def can(self, action: enums.Can) -> bool:
        """Check if user has the right permissions"""
        return action in self.permissions


    @staticmethod
    async def ban(*, authorization: 'Account', to_ban: 'Account', session: AsyncSession, notes: str = '') -> Union[
        'Account',
        None]:
        """
        Ban an account.
        :param authorization:   Account doing the ban
        :param to_ban:          Account to ban
        :param notes:           Reason for the ban
        :param session:         AsyncSession
        :return:                Account | None
        """
        if to_ban.is_banned:
            return

        if to_ban.is_user and not authorization.can(enums.Can.ban_user):
            raise ForbiddenException()
        elif to_ban.is_moderator and not authorization.can(enums.Can.ban_moderator):
            raise ForbiddenException()
        elif to_ban.is_admin and not authorization.can(enums.Can.ban_admin):
            raise ForbiddenException()
        elif to_ban.is_superadmin:
            raise ForbiddenException()
        elif authorization.uid == to_ban.uid:
            raise ForbiddenException('CANNOT_BAN_YOURSELF')

        if banned_account := await svc.AccountSvc.ban_user(authorization=authorization, to_ban=to_ban, notes=notes,
                                                           session=session):
            banned_account.update_cache(dict(is_banned=True))
            logger.info(msg=f'Ban account {banned_account.uid} by {authorization.uid}', id=banned_account.uid)
            return banned_account
        return


    @staticmethod
    async def unban(*, authorization: 'Account', to_unban: 'Account', session: AsyncSession) -> Union['Account', None]:
        """
        Unban an account.
        :param authorization:   Account doing the unban
        :param to_unban:        Account to unban
        :param session:         AsyncSession
        :return:                Account | None
        """
        if not to_unban.is_banned:
            return

        if to_unban.is_user and not authorization.can(enums.Can.ban_user):
            raise ForbiddenException()
        elif to_unban.is_moderator and not authorization.can(enums.Can.ban_moderator):
            raise ForbiddenException()
        elif to_unban.is_admin and not authorization.can(enums.Can.ban_admin):
            raise ForbiddenException()
        elif to_unban.is_superadmin:
            raise ForbiddenException()
        elif authorization.uid == to_unban.uid:
            raise ForbiddenException('CANNOT_UNBAN_YOURSELF')

        if account := await svc.AccountSvc.unban_user(authorization=authorization, to_ban=to_unban, session=session):
            account.update_cache(dict(is_banned=False))
            logger.info(msg=f'Unban account {account.uid} by {authorization.uid}', id=account.uid)
            return account
        return


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
