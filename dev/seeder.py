import os
import arrow
from fastapi import APIRouter
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from redis_om import get_redis_connection

from core import ic, SessionDep, Envs
from core.config import settings as s
from authentication import RoleCache, SystemOptionsCache, AccountSvc, Can, Role, Account
from models import auth_models as authmod
from models.common_models import OptionMod
from .data import SEED_ROLES, SEED_ACCOUNTS, SEED_SYSTEM_OPTIONS    # noqa


devrouter = APIRouter()


@devrouter.get('/seed')
async def seed(session: SessionDep) -> dict[str, int]:
    """Seed initial data to the db"""


    def _cache_system_options():
        cache = SystemOptionsCache(**{i['name']: i['value'] for i in SEED_SYSTEM_OPTIONS})
        cache.pk = 'system-options'
        cache.save()


    async def _user_custom_permissions():
        account = await AccountSvc.get_by_email('user1@mail.com', session=session)
        account.custom_permissions = [Can.ban_user.name]
        session.add(account)
        await session.commit()


    if os.getenv('ENV') == Envs.development:
        roles_count = await AppSeeder.generate_roles(session)
        account_count = await AppSeeder.generate_accounts(session)
        sys_options_count = await AppSeeder.generate_system_options(session)
        dd = dict(accounts=account_count, roles=roles_count, options=sys_options_count)

        _cache_system_options()
        await _user_custom_permissions()

        return dd


class AppSeeder:

    @classmethod
    async def generate_accounts(cls, session: AsyncSession) -> int:
        super_count = await cls._account_creator(SEED_ACCOUNTS['superadmin'], is_superadmin=True, session=session)
        admin_count = await cls._account_creator(SEED_ACCOUNTS['admin'], is_admin=True, session=session)
        moderator_count = await cls._account_creator(SEED_ACCOUNTS['moderator'], is_moderator=True, session=session)
        user_count = await cls._account_creator(SEED_ACCOUNTS['user'], session=session)
        return super_count + admin_count + moderator_count + user_count


    @staticmethod
    async def _account_creator(account_data: list[tuple], *, is_moderator: bool = False, is_admin: bool = False,
                               is_superadmin: bool = False, session: AsyncSession) -> int:
        count = 0

        stmt = select(Account.email)  # noqa
        exec_ = await session.exec(stmt)
        currentlist = exec_.all()

        for fields in account_data:
            d = dict(zip(['email', 'firstname', 'lastname', 'uid', 'provider'], fields))
            d.setdefault('is_banned', True if d['email'] == 'user2-banned@mail.com' else False)

            if d['email'] in currentlist:
                continue

            await Account.create(**d, is_moderator=is_moderator, is_admin=is_admin,
                                 is_superadmin=is_superadmin, session=session)
            count += 1

        return count


    @staticmethod
    async def generate_roles(session: AsyncSession) -> int:
        count = 0

        stmt = select(Role.name)  # noqa
        exec_ = await session.exec(stmt)
        currentlist = exec_.all()

        for name, perms in SEED_ROLES.items():
            if name in currentlist:
                continue

            role = Role(name=name, permissions=perms)  # noqa
            session.add(role)
            count += 1

            # Caching
            if s.USE_CACHE:
                cache = RoleCache(name=name, permissions=list(perms))
                cache.pk = name
                cache.save()

        if session.new:
            await session.commit()
        return count


    @staticmethod
    async def generate_system_options(session: AsyncSession):
        count = 0

        stmt = select(OptionMod.name).where(OptionMod.type == 1)
        exec_ = await session.exec(stmt)  # noqa
        currentlist = exec_.all()

        for i in SEED_SYSTEM_OPTIONS:
            if i['name'] in currentlist:
                continue

            option = OptionMod(name=i['name'], value=str(i['value']), type=1)
            session.add(option)
            count += 1

        # Caching
        if s.USE_CACHE:
            cache = SystemOptionsCache(**{i['name']: i['value'] for i in SEED_SYSTEM_OPTIONS})
            cache.pk = 'system-options'
            cache.save()

        if session.new:
            await session.commit()
        return count
