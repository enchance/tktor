import os
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.datastructures import State
# from redis_om import Migrator
from firebase_admin import credentials, initialize_app
from slowapi import Limiter, _rate_limit_exceeded_handler  # noqa
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core import ic
from core.config import settings as s
# from routes import accountrouter, authrouter
# from dev.seeder import devrouter
# from tests.routes import testrouter


limiter = Limiter(key_func=get_remote_address, default_limits=['120/minute'])


@asynccontextmanager
async def lifespan(_: FastAPI):
    ic('[STARTING_ACCOUNT...]')
    creds = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'))
    initialize_app(creds)
    ic('[Fireabase inititialized in Account]')

    # Migrator().run()
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

    # if s.DEBUG:
    #     app_.include_router(devrouter, prefix='/dev', tags=['dev'])
    #     app_.include_router(testrouter, prefix='/test', tags=['dev', 'test'])

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
