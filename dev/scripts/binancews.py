#!/usr/bin/env python3

import os, asyncio
from binance import AsyncClient, BinanceSocketManager
from icecream import ic


BINANCE_KEY = os.getenv('BINANCE_KEY')
BINANCE_SECRET = os.getenv('BINANCE_SECRET')


async def wss():
    async def handle_trade(msg):
        if msg['e'] == 'executionReport':  # Trade execution event
            ic(f"Trade: {msg['s']} | Side: {msg['S']} | Price: {msg['p']} | Qty: {msg['q']}")


    client = await AsyncClient.create(BINANCE_KEY, BINANCE_SECRET)
    bsm = BinanceSocketManager(client)

    try:
        async with bsm.user_socket() as stream:
            while True:
                msg = await stream.recv()
                await handle_trade(msg)
    except Exception as e:
        ic(e)


async def trade_history():
    client = await AsyncClient.create(BINANCE_KEY, BINANCE_SECRET)
    # bsm = BinanceSocketManager(client)

    account_trades = await client.get_account()
    # traded_symbols = {balance['asset'] + "USDT" for balance in account_trades['balances']}  # Adjust for different pairs
    traded_symbols = {bal['asset']: bal for bal in account_trades['balances'] if float(bal['free'])}
    ic(traded_symbols)

    # Fetch trades for each symbol
    # tasks = [client.get_my_trades(symbol=symbol) for symbol in traded_symbols]
    # all_trades = await asyncio.gather(*tasks, return_exceptions=True)
    # ic(all_trades[0])


if __name__ == '__main__':
    asyncio.run(trade_history())
