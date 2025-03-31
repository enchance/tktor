from typing import TYPE_CHECKING, Union
from sqlmodel import update, select, func
from sqlalchemy.ext.asyncio.session import AsyncSession

from core import NotFoundException, logger
from core.config import settings as s
from .Auth import Account, Role, BanMod


class RoleSvc:
    # TESTME: Untested
    @classmethod
    async def get_by_name(cls, name: str, *, session: AsyncSession) -> Union['Role', None]:
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
        :param uid:     Account uid
        :param session: AsyncSession
        :return:        Account
        :raises:        NotFoundException
        """
        try:
            stmt = select(Account).where(Account.uid == uid)
            exec_ = await session.exec(stmt)
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
        :param email:   Account email
        :param session: AsyncSession
        :return:        Account
        :raises:        NotFoundException
        """
        try:
            stmt = select(Account).where(Account.email == email)
            exec_ = await session.exec(stmt)  # type: ignore
            if account := exec_.one_or_none():
                return account
            raise NotFoundException('ACCOUNT_NOT_FOUND')
        except Exception as _:
            logger.warning(dict(message=f"Account {email} not found", id=email))
            raise


    @staticmethod
    async def get_options(id_: int, *, session: AsyncSession) -> dict[str, str]:
        """
        Get options for an account.
        :param id_:         Account ID
        :param session:     AsyncSession
        :return:
        """
        stmt = select(models.Option.name, models.Option.value).where(models.Option.owner_id == id_)  # noqa
        exec_ = await session.exec(stmt)
        if data := exec_.all():
            return dict(data)
        return {}


    @staticmethod
    async def update(uid: str, to_save: dict, *, session: AsyncSession) -> bool:
        """
        Update an Account instance.
        :param uid:         Account uid
        :param to_save:     Data to save
        :param session:     AsyncSession
        :return:            bool
        """
        if not to_save:
            return False
        stmt = update(Account).where(Account.uid == uid).values(**to_save)  # noqa
        await session.exec(stmt)
        await session.commit()
        return True


    @staticmethod
    async def is_unique_email(email: str, *, session: AsyncSession) -> bool:
        """
        Check if an Account email is unique.
        :param email:       Email address to verify
        :param session:     AsyncSession
        :return:            bool
        """
        stmt = select(Account.uid).where(Account.email == email)
        exec_ = await session.exec(stmt)
        if _ := exec_.one_or_none():
            logger.warn(dict(message=f"Account {email} not found", id=email))
            return False
        return True


    @staticmethod
    async def is_unique_username(username: str, *, session: AsyncSession) -> bool:
        """
        Check if an Account username is unique.
        :param username:    Username to verify
        :param session:     AsyncSession
        :return:            bool
        """
        try:
            stmt = select(Account.uid).where(Account.username == username)
            exec_ = await session.exec(stmt)
            if _ := exec_.one_or_none():
                logger.warn(dict(message=f"Account {username} not found", id=username))
                return False
            return True
        except Exception as e:
            logger.error(dict(message=str(e)))
            if s.DEBUG:
                raise e
            return False


    @staticmethod
    async def ban_user(*, authorization: 'Account', to_ban: 'Account', notes: str,
                       session: AsyncSession) -> Account:  # noqa
        """
        Ban an account.
        :param authorization:   Account that does the banning
        :param to_ban:          Account to ban
        :param notes:           Reason for the ban
        :param session:         AsyncSession
        :return:                Banned account
        """
        try:
            ban = BanMod(recipient_id=to_ban.id, owner_id=authorization.id, notes=notes)
            session.add(ban)

            stmt = update(Account).where(Account.id == to_ban.id).values(is_banned=True)  # noqa
            await session.exec(stmt)
            await session.commit()

            to_ban.is_banned = True
            return to_ban
        except Exception as e:
            logger.error(dict(message=f"Failed to ban account {to_ban.id} authorized by {authorization.id}",
                              id=to_ban.id, extra=str(e)))
            raise e


    @staticmethod
    async def unban_user(*, authorization: 'Account', to_ban: 'Account',
                         session: AsyncSession) -> (Account):  # noqa
        """
        Unban an account.
        :param authorization:   Account that does the banning
        :param to_ban:          Account to unban
        :param session:         AsyncSession
        :return:                Unbanned account
        """
        try:
            stmt = (update(BanMod)
                    .where(BanMod.recipient_id == to_ban.id, BanMod.owner_id == authorization.id,  # noqa
                           BanMod.is_active == True)  # noqa
                    .values(is_active=False))  # noqa
            await session.exec(stmt)  # noqa

            stmt = update(Account).where(Account.id == to_ban.id).values(is_banned=False)  # noqa
            await session.exec(stmt)
            await session.commit()

            to_ban.is_banned = False
            return to_ban

        except Exception as e:
            logger.error(dict(message=f"Failed to ban account {to_ban.id} authorized by {authorization.id}",
                              id=to_ban.id, extra=str(e)))
            raise e
