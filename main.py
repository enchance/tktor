import os
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.datastructures import State
from redis_om import Migrator
from firebase_admin import credentials, initialize_app
from slowapi import Limiter, _rate_limit_exceeded_handler  # noqa
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import select
from sqlalchemy.orm import selectinload

from core import ic
from core.config import settings as s
from authentication import Account
from core import SessionDep
from models.auth_models import ProfileMod, AddressMod
from models.common_models import Option
# from routes import accountrouter, authrouter
from dev.seeder import devrouter
from tests.routes import testrouter


# TODO: Review the test to ban/unban as the fields have changed


limiter = Limiter(key_func=get_remote_address, default_limits=['120/minute'])


@asynccontextmanager
async def lifespan(_: FastAPI):
    ic('[STARTING_ACCOUNT...]')
    creds = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'))
    initialize_app(creds)
    ic('[Fireabase inititialized in Account]')

    Migrator().run()
    ic('[STARTUP_ACCOUNT_COMPLETE]')
    yield
    ic('[SHUTDOWN_ACCOUNT_COMPLETE]')


def get_app(data: dict) -> FastAPI:
    configmap = {
        'title': s.SITENAME,
        'version': s.VERSION,
        'lifespan': lifespan,
    }

    if not s.DEBUG:
        configmap['docs_url'] = None
        configmap['redoc_url'] = None
        configmap['swagger_ui_oauth2_redirect_url'] = None

    app_ = FastAPI(**configmap)

    # CORS
    origins = set()
    if s.DEBUG:
        origins = {'http://localhost:5173', 'https://*.ngrok.io/'}

    app_.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    app_.add_middleware(SlowAPIMiddleware)  # noqa
    # app_.include_router(accountrouter, prefix='/account', tags=['account'])
    # app_.include_router(authrouter, prefix='/auth', tags=['auth'])

    if s.DEBUG:
        app_.include_router(devrouter, prefix='/dev', tags=['dev'])
        app_.include_router(testrouter, prefix='/test', tags=['dev', 'test'])

    app_.state = State(state=data)
    app_.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # noqa

    return app_


app = get_app({
    'hello': 'world',
    'limiter': limiter
})


@app.get('/')
@limiter.limit('3/minute')
async def root(request: Request):
    return 'Account Service'


@app.get('/healthz-app')
async def healthz(request: Request):
    # ic('healthz')
    return Response(status_code=200)


@app.get('/foo')
async def foo(request: Request, session: SessionDep):
    account = Account(
        email='aaa@aaa.com', username='aaa', display='aaa', avatar='', uid='anoeutsiht',
        profile=ProfileMod(firstname='haha', mobile=['123', '456']),
        addresses=[
            AddressMod(),
            AddressMod(),
        ],
        options_rel=[
            Option(name='foo', value='bar')
        ]
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)
    ic(type(account), account)

    stmt = select(Account).where(Account.email == 'aaa@aaa.com') \
        .options(selectinload(Account.profile), selectinload(Account.bans_received), selectinload(Account.addresses),
                 selectinload(Account.options_rel))
    exec_ = await session.exec(stmt)
    account = exec_.one_or_none()

    # opts = OptionMod(name='hey', value='you', account=account)
    # account.options_rel.append(opts)
    # session.add(account)
    # await session.commit()
    # await session.refresh(account)

    # await session.refresh(account, attribute_names=['profile'])
    # account.profile.firstname = 'boo'
    # session.add(account.profile)
    # await session.commit()
    # profile: ProfileMod = account.profile
    ic(account.bans_received, account.profile.firstname, account.addresses, account.options_rel)

    # profile = await session.get(ProfileMod, 5)
    # ic(profile.account)

    return True
