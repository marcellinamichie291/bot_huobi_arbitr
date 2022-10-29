import asyncio
import json
import logging
import websockets


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
    filename='log.log'
    )


WS_URL = 'wss://api.huobi.pro/ws'








async def my_loop_WebSocket_bybit(event):

    async with websockets.connect(WS_URL) as websocket:
        # await websocket.send(get_args_secret(BYBIT_API, BYBIT_SECRET)) # secret 


        print("Connected to bybit WebSocket with secret key")
        params = {
            "sub": "market.btcusdt.ticker"
        }
        await websocket.send(json.dumps(params))

        while True:
            if event.is_set():
                logging.info('Выходим из цикла...')
                break
            json_str = await websocket.recv()








async def main():
    event = asyncio.Event()
    tasks_list = [asyncio.create_task(my_loop_WebSocket_bybit(event)) for _ in range(2)]
    await asyncio.gather(*tasks_list)



if __name__ == '__main__':
    asyncio.run(main())












