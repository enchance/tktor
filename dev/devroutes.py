import os, asyncio, pytz
from datetime import datetime as dt
import pandas as pd
from fastapi import APIRouter
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from binance import AsyncClient
from dotenv import load_dotenv

from core import ic, SessionDep, Envs
from core.config import settings as s
from authentication import RoleCache, SystemOptionsCache, AccountSvc, Can, Role, Account
from exchange import Exchange
from core.models import Option
from exchange.Trades import Order, Trade
from exchange import TradeSvc
from .data import SEED_ROLES, SEED_ACCOUNTS, SEED_SYSTEM_OPTIONS, SEED_EXCHANGES, SEED_SYMBOLS  # noqa


load_dotenv()
BINANCE_KEY = os.getenv('BINANCE_KEY')
BINANCE_SECRET = os.getenv('BINANCE_SECRET')
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
        exchanges_count = await AppSeeder.seed_exchanges(session=session)

        # SQL populated
        order_count = await AppSeeder.seed_orders(session)
        trade_count = await AppSeeder.seed_trades(session=session)

        _cache_system_options()
        await _user_custom_permissions()

        dict_ = dict(
            accounts=account_count, roles=roles_count, options=sys_options_count, exchanges=exchanges_count,
            orders=order_count, trades=trade_count
        )

        return dict_


# @devrouter.get('/fill')
# async def fetch_orders(session: SessionDep):
#     await AppSeeder.seed_orders(session)
#     await AppSeeder.seed_trades(session=session)


# @devrouter.get('/foo')
# async def foo(session: SessionDep):
#     stmt = select(Account)
#     exec_ = await session.exec(stmt)
#     accounts = exec_.all()
#     for i in accounts:
#         ic(i.model_dump())


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

        stmt = select(Option.name).where(Option.type == 1)
        exec_ = await session.exec(stmt)  # noqa
        currentlist = exec_.all()

        for i in SEED_SYSTEM_OPTIONS:
            if i['name'] in currentlist:
                continue

            option = Option(name=i['name'], value=str(i['value']), type=1)
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


    @staticmethod
    async def seed_exchanges(session: AsyncSession):
        stmt = select(Exchange.name)
        exec_ = await session.exec(stmt)
        current = set(exec_.all())

        total = 0
        for i in SEED_EXCHANGES:
            if i['name'] in current:
                continue
            session.add(Exchange(**i))
            total += 1
        if session.new:
            await session.commit()
        return total


    @staticmethod
    async def seed_orders(session: AsyncSession):
        def _clean_orders(df_: pd.DataFrame):
            df_['time'] = pd.to_datetime(df_['time'], unit='ms')
            df_['updateTime'] = pd.to_datetime(df_['updateTime'], unit='ms')
            df_['workingTime'] = pd.to_datetime(df_['workingTime'], unit='ms')
            df_ = df_.drop(columns=['workingTime', 'selfTradePreventionMode', 'isWorking', 'orderListId'])
            df_ = df_.rename(columns={
                'orderId': 'exchange_orderid',
                'clientOrderId': 'client_orderid',
                'price': 'stop_limit',
                'origQty': 'amount',
                'executedQty': 'executed_amount',
                'cummulativeQuoteQty': 'cum_quote_amount',
                'timeInForce': 'time_in_force',
                'stopPrice': 'stop_price',
                'icebergQty': 'iceberg_amount',
                'origQuoteOrderQty': 'quote_amount',
                'time': 'created_at',
                'updateTime': 'updated_at',
            })
            return df_


        # Current
        stmt = select(Order.id)
        exec_ = await session.exec(stmt)
        current = exec_.all()
        if current:
            return 0

        account = await AccountSvc.get_by_email(os.getenv('DEV_EMAIL_ADMIN'), session=session)
        binance = await TradeSvc.get_exchange('binance', session=session)
        client = await AsyncClient.create(BINANCE_KEY, BINANCE_SECRET)

        tasks = []
        for symbol in SEED_SYMBOLS:
            tasks.append(client.get_all_orders(symbol=symbol))
        results = await asyncio.gather(*tasks)

        fulldf = pd.DataFrame()
        for i in results:
            df = pd.DataFrame(i)
            fulldf = pd.concat([fulldf, df], axis=0)
        fulldf = _clean_orders(fulldf)

        total = 0
        for row in fulldf.itertuples(index=True):
            dd = row._asdict()  # noqa
            del dd['Index']
            dd['created_at'] = dd['created_at'].to_pydatetime().replace(tzinfo=pytz.utc)
            dd['updated_at'] = dd['updated_at'].to_pydatetime().replace(tzinfo=pytz.utc)
            dd['id'] = f"{binance.prefix}_{dd['exchange_orderid']}"
            # dd['id'] = str(dd['id'])
            order = Order(**dd, exchange=binance, account=account)
            session.add(order)
            total += 1

        if session.new:
            await session.commit()
        return total


    @staticmethod
    async def seed_trades(session: AsyncSession):
        # Current
        stmt = select(Trade.id)
        exec_ = await session.exec(stmt)
        current = exec_.all()
        if current:
            return 0

        account = await AccountSvc.get_by_email(os.getenv('DEV_EMAIL_ADMIN'), session=session)
        binance = await TradeSvc.get_exchange('binance', session=session)
        client = await AsyncClient.create(BINANCE_KEY, BINANCE_SECRET)

        tasks = []
        # symbol = 'BANANAUSDT'
        for symbol in SEED_SYMBOLS:
            tasks.append(client.get_my_trades(symbol=symbol))
        trades = await asyncio.gather(*tasks, return_exceptions=True)

        # stmt = select(Order)
        # exec_ = await session.exec(stmt)
        # orderlist = exec_.all()

        total = 0
        for i in trades:
            for t in i:
                order_id = f"{binance.prefix}_{t['orderId']}"
                trade = Trade(
                    id=f"{binance.prefix}_{t['id']}",
                    exchange_orderid=order_id,
                    price=t['price'],
                    symbol=t['symbol'],
                    commission=t['commission'],
                    asset=t['commissionAsset'],
                    is_best_match=t['isBestMatch'],
                    is_buyer=t['isBuyer'],
                    is_maker=t['isMaker'],
                    amount=t['qty'],
                    total=t['quoteQty'],
                    exchange_id=binance.id,
                    order_id=order_id,
                    account_id=account.id,
                    created_at=dt.fromtimestamp(t['time'] / 1000, tz=pytz.utc),
                )
                # for order in orderlist:
                #     if order.id == trade.exchange_orderid:
                #         trade.order_id = order.id
                #         # ic(trade.model_dump())
                #         break

                # ic(trade.model_dump())
                session.add(trade)
                total += 1

        if session.new:
            await session.commit()
        return total


    @staticmethod
    async def account_info(session: AsyncSession):
        client = await AsyncClient.create(BINANCE_KEY, BINANCE_SECRET)
        trades = await client.get_account()
        # ic(trades['balances'])

        # ll = []
        dict_ = {}
        for i in trades['balances']:
            if float(i['free']) or float(i['locked']):
                dict_[i['asset']] = {'locked': i['locked'], 'free': i['free']}
            # ll.append(i['asset'])
        # ic(len(ll), len(set(ll)))
        ic(dict_)
