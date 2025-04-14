from pytest import mark
from sqlmodel import select

from core import ic
from exchange import APIKeys, ExchangeSvc


class TestExchange:
    async def setup(self):
        pass

    # @mark.focus
    async def test_get_apikeys(self, session, make_apikeys, exchange_fetcher):
        binance, coinsph, coinbase = exchange_fetcher
        acct_, key1, key2, key3, key4 = await make_apikeys([binance, binance, coinsph, coinbase])

        keys = await APIKeys.get(acct_, session=session)
        assert len(keys) == 3
        keys = await APIKeys.get(acct_, only_active=True, session=session)
        assert len(keys) == 3
        keys = await APIKeys.get(acct_, only_active=False, session=session)
        assert len(keys) == 1
        keys = await APIKeys.get(acct_, only_active=None, session=session)
        assert len(keys) == 4

        keys = await APIKeys.get(acct_, only_active=None, session=session, limit=1)
        assert len(keys) == 1
        keys = await APIKeys.get(acct_, only_active=None, session=session, limit=2)
        assert len(keys) == 2

        keys = await APIKeys.get(acct_, 'binance', session=session)
        assert len(keys) == 2
        keys = await APIKeys.get(acct_, 'binance', only_active=True, session=session)
        assert len(keys) == 2
        keys = await APIKeys.get(acct_, 'binance', only_active=False, session=session)
        assert not len(keys)
        keys = await APIKeys.get(acct_, 'binance', only_active=None, session=session)
        assert len(keys) == 2

        keys = await APIKeys.get(acct_, 'coinbase', session=session)
        assert not len(keys)
        keys = await APIKeys.get(acct_, 'coinbase', only_active=True, session=session)
        assert not len(keys)
        keys = await APIKeys.get(acct_, 'coinbase', only_active=False, session=session)
        assert len(keys) == 1
        keys = await APIKeys.get(acct_, 'coinbase', only_active=None, session=session)
        assert len(keys) == 1
