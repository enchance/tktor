import os, arrow
from enum import StrEnum  # noqa
from pytest import mark  # noqa
from secrets import token_hex  # noqa
from faker import Faker  # noqa
from sqlmodel import select  # noqa
from sqlalchemy.orm import selectinload  # noqa
from functools import reduce  # noqa

from core import ic, Envs
from models.common_models import OptionMod
from core.config import get_session_context
# from account import AccountSvc, Token
from auth import Account, Role, AccountCache, UserOptions

fake = Faker()


class TestDev:
    @mark.dev
    async def test_dev(self, session):
        try:
            # account = await Account.create(uid=token_hex(14), email=fake.email(), avatar=fake.image_url(),
            #                                firstname=fake.first_name(), lastname=fake.last_name(), website=fake.url(),
            #                                username=fake.user_name(), display=fake.word(), gender='male',
            #                                social=dict(a='b', c=24), provider='google', session=session)
            # ic(account)

            foo = arrow.get(1660801715793)
            ic(type(foo), foo)


            # x = {'comment_order': 'desc',
            #      'comment_publish_delay': '120',
            #      'comments_blacklist': '',
            #      'comments_per_page': '10',
            #      'date_format': '%b %d, %Y',
            #      'items_per_page': '10',
            #      'max_upload_mb': '5',
            #      'time_format': '%I:%M%p',
            #      'timezone': 'UTC'}
            # x = UserOptions(**x)
            # ic(x)


            # stmt = select(Account.is_verified).where(Account.uid == os.getenv('DEV_UID_ADMINx'))  # noqa
            # exec_ = await session.exec(stmt)
            # data = exec_.one_or_none()
            # ic(data)

            # stmt = select(Option.name, Option.value).where(Option.owner_id == 1)  # noqa
            # exec_ = await session.exec(stmt)  # noqa
            # data = exec_.all()
            # ic(dict(data))

            # account = await AccountSvc.get_by_email('obutler@example.com', session=session)
            # account = await AccountSvc.get_by_uid('9df68967c33acdca8fa812da0925', session=session)
            # ic(account.model_dump())

            # rolelist = await AccountSvc.get_roles(['upload', 'user'], session=session)

            # account = await Account.get(account_.uid, session=session)
            # ic(account)
            # await session.refresh(account, attribute_names=['roles_rel'])
            # ic(account.roles_rel)

            # stmt = select(Role.permissions).where(Role.name.in_(['upload', 'user']))  # noqa
            # exec_ = await session.exec(stmt)  # noqa
            # data = exec_.all()
            # ic(data)
            # ic(list(set(reduce(lambda x, y: x + y, data))))
            # data = await AccountSvc.get_permissions(['upload', 'user'], session=session)
            # ic(data)

            # stmt = select(Account).options(selectinload(Account.roles_rel)).where(Account.id == account_.id)    # noqa

            # stmt = select(Account).where(Account.id == 1)    # noqa
            # exec_ = await session.exec(stmt)
            # if account := exec_.one_or_none():
            #     await session.refresh(account, attribute_names=['roles_rel'])
            #     ic(account.roles_rel)

            #     # await session.refresh(account, attribute_names=['role_rel'])
            #     ic(account.roles_rel)
            # ic('has_account')
            # # account.roles_rel = rolelist
            # session.add(account)
            # await session.commit()
            # await session.refresh(account)
            # ic(account)
            # ic(account.roles_rel)

            # cache = AccountCache.get(account.uid)
            # ic(cache)
            # account2 = cache.to_account()
            # ic(account2)
            # ic(account2.options)

            # ic(account, account.gender, account.social, account.provider)
            # ic(account.fullname)
            # ic(account.options)

            # stmt = select(Role.name).where(Role.)

            # cache_data = AccountCache.get(account.uid)
            # ic(cache_data)

            # ic(set(Account.model_fields.keys()))    # noqa
            # account = await AccountSvc.get_by_uid('3Qc1pDX7chSNpo9LjGhp3hQvZLp2', session)
            # accounts = await AccountSvc.get_by_uid('3Qc1pDX7chSNpo9LjGhp3hQvZLp2')
            # ic(accounts)

            return True
        except Exception as e:
            ic(e)
