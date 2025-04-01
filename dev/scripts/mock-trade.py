#!/usr/bin/env python3

import asyncio, os
from binance import AsyncClient, BinanceSocketManager
from icecream import ic

# BINANCE_KEY = os.getenv('BINANCE_KEY')
# BINANCE_SECRET = os.getenv('BINANCE_SECRET')

async def handle_trade(msg):
    if msg['e'] == 'executionReport':
        print(f"Trade: {msg['s']} | Side: {msg['S']} | Price: {msg['p']} | Qty: {msg['q']}")

# Mock trade message
mock_trade = {
    'e': 'executionReport',  # Event type
    'E': 1698765432100,      # Event time (ms)
    's': 'BTCUSDT',          # Symbol
    'S': 'BUY',              # Side
    'p': '30000.00',         # Price
    'q': '0.005',            # Quantity
    'X': 'FILLED',           # Order status
    'i': 123456789           # Order ID (fake)
}

async def main():
    # client = await AsyncClient.create(BINANCE_KEY, BINANCE_SECRET)
    await handle_trade(mock_trade)
    # Uncomment below to run real WebSocket after testing
    """
    client = await AsyncClient.create('your_api_key', 'your_api_secret')
    bsm = BinanceSocketManager(client)
    async with bsm.user_socket() as stream:
        while True:
            msg = await stream.recv()
            await handle_trade(msg)
    """

asyncio.run(main())