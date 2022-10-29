import gzip
import json
import time

from sqlalchemy.orm import sessionmaker

from config import engine
from models import CurrencyPair
import websocket


WS_URL = 'wss://api.huobi.pro/ws'


def on_open(ws):
    print("Opened connection")

    Session = sessionmaker(bind=engine)
    session = Session()
    
    for pair in session.query(CurrencyPair):
        ticker = pair.pair.replace('/', '').lower()
        ws.send(json.dumps({"sub": f"market.{ticker}.ticker"}))




def handle_invalid_symbol(ws, session, data):
    ticker = data['err-msg'].split()[-1].upper()

    pair = (
        session.query(CurrencyPair)
        .filter_by(ticker=ticker)
        .first()
    )
    pair.status = 'invalid symbol'

    # проверяем или в базе есть перевёрнутая пара
    rev_pair = '/'.join(reversed(pair.pair.split('/')))
    reversed_pair = (
        session.query(CurrencyPair)
        .filter_by(pair=rev_pair)
        .first()
    )
    if reversed_pair:
        pair.rate = 1 / reversed_pair.rate

    else:
        reversed_pair = CurrencyPair(
            pair=rev_pair,
            ticker=rev_pair.replace('/', '')
        )
        session.add(reversed_pair)

        ticker = rev_pair.replace('/', '').lower()
        ws.send(json.dumps({"sub": f"market.{ticker}.ticker"}))



def update_invalid_symbols():
    """
    Обновляет перевёрнутые пары
    """
    pass



def on_message(ws, message):
    data = json.loads(gzip.decompress(message))

    Session = sessionmaker(bind=engine)
    session = Session()
    
    if 'ping' in data:
        ws.send(json.dumps({'pong': data['ping']}))
        print('send PONG')

    elif 'ch' in data:
        ticker = data['ch'].replace('market.', '').replace('.ticker', '')
        price = data['tick']['lastPrice']
        print(price)


        pair = (
            session.query(CurrencyPair)
            .filter_by(ticker=ticker.upper())
            .first()
        )
        pair.rate = price




    elif 'subbed' in data:
        print(f'Подписались на канал: {data["subbed"]}')
    elif 'err-msg' in data and 'invalid symbol' in data['err-msg']:
        print(data['err-msg'])
        handle_invalid_symbol(ws, session, data)
        # pass
    else:
        print(f'Неизвестный ответ сервера: {data}')


    session.commit()
    session.close()



def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")




if __name__ == "__main__":
    ws = websocket.WebSocketApp(WS_URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever()
