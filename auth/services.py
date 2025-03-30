from typing import TYPE_CHECKING, Union
from sqlalchemy.ext.asyncio.session import AsyncSession

from core import NotFoundException, logger
from .Auth import Account, Role


class RoleSvc:
    @classmethod
    async def get_by_name(cls, name: str, *, session: AsyncSession) -> Union['Role', None]:  # noqa
        """
        Get a role by its name.
        :param name:        Role name
        :param session:     AsyncSession
        :return:            Role
        """
        return await session.get(Role, name)


class AccountSvc:
    @staticmethod
    async def get_by_uid(uid: str, *, session: AsyncSession) -> Account:
        """
        Return an Account instance by its uid.
        :param uid:             Account uid
        :param session:         AsyncSession
        :return:                Account
        """
        try:
            stmt = select(Account).where(Account.uid == uid)  # noqa
            exec_ = await session.exec(stmt)  # noqa
            if account := exec_.one_or_none():
                return account
            raise NotFoundException('ACCOUNT_NOT_FOUND')
        except Exception as _:
            logger.warning(dict(message=f"Account {uid} not found", id=uid))
            raise


    @staticmethod
    async def get_by_email(email: str, *, session: AsyncSession) -> Account:
        """
        Return an Account instance by its email.
        :param email:           Account email
        :param session:         AsyncSession
        :return:                Account
        """
        try:
            stmt = select(Account).where(Account.email == email)  # noqa
            exec_ = await session.exec(stmt)  # type: ignore
            if account := exec_.one_or_none():
                return account
            raise NotFoundException('ACCOUNT_NOT_FOUND')
        except Exception as _:
            logger.warning(dict(message=f"Account {email} not found", id=email))
            raise
