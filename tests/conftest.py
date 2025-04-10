import os, random, httpx, pytest
from typing import Callable, Awaitable, TYPE_CHECKING
from secrets import token_hex
from redis_om import get_redis_connection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from faker import Faker
from slugify import slugify
from dotenv import load_dotenv

from main import app
from core import ic  # noqa
from authentication import Auth as auth
from authentication import schemas
from core.models import Taxonomy


load_dotenv()
fake = Faker()

if TYPE_CHECKING:
    from authentication import Account, Role


@pytest.fixture
def async_engine():
    return create_async_engine(os.getenv('POSTGRES_URL'), echo=False, future=True)


@pytest.fixture
async def session(async_engine):
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client():
    # async with TestClient(app) as tc:
    #     yield tc
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test/") as ac:
        yield ac


@pytest.fixture
def redis_conn():
    return get_redis_connection()


@pytest.fixture
async def account_(session) -> 'Account':
    account = await auth.Account.create(uid=token_hex(14), email=fake.email(), avatar=fake.image_url(),
                                        firstname=fake.first_name(), lastname=fake.last_name(),
                                        username=fake.user_name(),
                                        display=fake.word(), gender='male', social=dict(a='b', c=24),
                                        provider='fake-provider', website=fake.url(), session=session)
    await session.refresh(account, attribute_names=['profile'])
    yield account
    schemas.AccountCache.delete(account.uid)
    await session.delete(account)
    await session.commit()


@pytest.fixture()
def account_factory() -> Callable[..., Awaitable['Account']]:
    async def foo(*, is_moderator: bool = False, is_admin: bool = False, is_superadmin: bool = False,
                  session: AsyncSession) -> 'Account':
        return await auth.Account.create(uid=token_hex(14), email=fake.email(), avatar=fake.image_url(),
                                         firstname=fake.first_name(), lastname=fake.last_name(),
                                         username=fake.user_name(),
                                         display=fake.word(), gender='male', social=dict(facebook=fake.url()),
                                         provider='fake-provider', website=fake.url(), is_moderator=is_moderator,
                                         is_admin=is_admin, is_superadmin=is_superadmin, session=session)


    return foo


@pytest.fixture
async def generate_accounts(redis_conn, account_factory, session):
    user = await account_factory(session=session)
    moderator = await account_factory(is_moderator=True, session=session)
    admin = await account_factory(is_admin=True, session=session)
    superadmin = await account_factory(is_superadmin=True, session=session)

    yield user, moderator, admin, superadmin

    redis_conn.delete(f'user:{user.uid}')
    schemas.AccountCache.delete(user.uid)
    schemas.AccountCache.delete(moderator.uid)
    schemas.AccountCache.delete(admin.uid)
    schemas.AccountCache.delete(superadmin.uid)
    await session.delete(user)
    await session.delete(moderator)
    await session.delete(admin)
    await session.delete(superadmin)
    await session.commit()


@pytest.fixture
async def role_(redis_conn, session) -> 'Role':
    actions = ['eat', 'sleep', 'buy', 'write', 'check', 'ban', 'create', 'ignore']
    permissions = {f'{random.choice(actions)}.{fake.word()}' for _ in range(3)}
    role = auth.Role(name=fake.word(), permissions=permissions)  # noqa

    session.add(role)
    await session.commit()
    auth.Role.set_cache(role.name, role.permissions)
    yield role
    redis_conn.delete(f'role:{role.name}')
    await session.delete(role)
    await session.commit()


@pytest.fixture(scope='session')
def valid_token():
    return os.getenv('DEV_TOKEN_VALID')


@pytest.fixture(scope='session')
def invalid_token():
    return 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImE3MWI1MTU1MmI0ODA5OWNkMGFkN2Y5YmZlNGViODZiMDM5NmUxZDEiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiRW5jaGFuY2UiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTDYzcmNHVFBqRjMya082LXp1RkdwNWlzVUVLVEhnd2pOYjdpOE5Rc0NzTnhfeFNrR2s9czk2LWMiLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vc2FuZGJveDItNzg0NTgiLCJhdWQiOiJzYW5kYm94Mi03ODQ1OCIsImF1dGhfdGltZSI6MTczNTMwNDQ2MSwidXNlcl9pZCI6IkdqSW5yU2w5MHFWSU1aVFBMcFFRZ3VqVVI2NDMiLCJzdWIiOiJHakluclNsOTBxVklNWlRQTHBRUWd1alVSNjQzIiwiaWF0IjoxNzM1MzA0NDYxLCJleHAiOjE3MzUzMDgwNjEsImVtYWlsIjoiZW5jaGFuY2VAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMDE0MjYwMjQ4Njk1MzU1NzQyOTEiXSwiZW1haWwiOlsiZW5jaGFuY2VAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.FQkH09XGN-42vQmRt9KbZ8p5GlzP-wvTIiLRo3NNzT6eAsEeghm5AkvJ3lsM6NjthDLCq67RFnbJ1vUR0PhTve3wbFH8ejLpyQc2voZBZRx5JNKQxGFW16-vcUPHyjFshnQ7_9Db2VYsyOl_gdyQkBgfyaBeyFvO8Mbd7WvMY3w-o84ZBAoJKh9j_y-9_uci2cxtml4hWb1YiuWFt1nX0leiNUcN8w3Bcm1hATMUYZfKjGuFoaog5qS9z6p5EcGH4v64VVuVicFW-HxOknU_0wpMiOiyzLJaxp3sf7dm6gpZ84lzdrjM0TVCcheE3mQ29WmyQG3URhYFzHok5ucxxx'


@pytest.fixture
def bearer_token() -> str:
    token = os.getenv('DEV_TOKEN_VALID')
    return f'Bearer {token}'
    # return 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjBhYmQzYTQzMTc4YzE0MjlkNWE0NDBiYWUzNzM1NDRjMDlmNGUzODciLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSi5NLiBJbWJvbmciLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSU5LVWI5TUtqak44d1JqTVRMdkJtajl1M0lCVXlFbEJ1cnRZSEFxS2QxR0J5SEh1QW89czk2LWMiLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vc2FuZGJveDItNzg0NTgiLCJhdWQiOiJzYW5kYm94Mi03ODQ1OCIsImF1dGhfdGltZSI6MTczNzEwMzM2OSwidXNlcl9pZCI6Im9pbU1UNm9jN3ZjcEJhM1psdzZ0TmZEd1NyRDMiLCJzdWIiOiJvaW1NVDZvYzd2Y3BCYTNabHc2dE5mRHdTckQzIiwiaWF0IjoxNzM3MTAzMzY5LCJleHAiOjE3MzcxMDY5NjksImVtYWlsIjoiam9obi5pbWJvbmdAbWludGNvbGxlZ2UuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMDY1NDQzNTA2NTMzNTk2NDg3MDkiXSwiZW1haWwiOlsiam9obi5pbWJvbmdAbWludGNvbGxlZ2UuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.BUwCUQi2BIuD-yf2eG7jqDFuQEQHypbgSMjpkK8l0Q2byVaHjphQXyFH82Dc7yPF1hmQEcz2Of7vIkVKsC2f0sFQOe7WY0ZXOQfE8YtCrQg1N2fDDSUH_zTYMI8YnrkxvyEGYiXmcjofuGDPdv0Y_wQjimSyxrHwTIWkFk2TQIvgCeKN0f-_MyYSHU6oOl5w1tFvAmZ1reHO5u92q4BH2GVET2LnujsvyTpFFss24pdF8BN_9rsAhPNVsvyQakxZ_iw1nm4yNdC40XcZOKGTaP4y9E8sdAtj0bTLYL51yqTz5tXXNPMR772uNOARH1JsgWmyDsuAbFd7H_GFzEUmag'


@pytest.fixture
def make_taxonomy(session):
    async def func(*, name: str, account: 'Account', slug: str = '', parent: ['Account', None] = None) -> 'Taxonomy':
        tax = Taxonomy(name=name, slug=slug, account=account, parent=parent)
        session.add(tax)
        await session.commit()
        # await session.refresh(tax, ['children'])
        return tax


    return func


@pytest.fixture
async def taxonomy_(session, account_, make_taxonomy):
    parent = await make_taxonomy(name=f'{fake.first_name()} {fake.last_name()}', account=account_)
    child = await make_taxonomy(name=f'{fake.first_name()} {fake.last_name()}', account=account_, parent=parent)
    return child
    # schemas.AccountCache.delete(parent.uid)
    # schemas.AccountCache.delete(child.uid)
    # await session.delete(parent)
    # await session.delete(child)
    # await session.commit()
