from pybit.inverse_perpetual import HTTP
import time
import json


API_NAME = "API_NAME"
API_SECRET = "API SECRET"
API_KEY = "API KEY"
BASE_ENDPOINT = "https://api-testnet.bybit.com"
SESSION = HTTP(BASE_ENDPOINT, api_key=API_KEY, api_secret=API_SECRET)


def get_price(ticker, interval, limit):
    res = SESSION.query_mark_price_kline(
        symbol=ticker,
        interval=interval,
        limit=limit,
        from_time=int(time.time()) - 60 * 60 * 24,
    )

    return None if res["ret_code"] else res["result"]


def set_leverage(ticker, leverage):
    res = SESSION.set_leverage(symbol=ticker, leverage=leverage)
    return None if res["ret_code"] else True


def get_active_orders(ticker, order_status="Filled", limit=1):
    res = SESSION.get_active_order(
        symbol=ticker, order_status=order_status, limit=limit
    )

    return None if res["ret_code"] else res["result"]  # result["data"][{},{},{}]


def get_position(ticker):
    res = SESSION.my_position(symbol=ticker)
    return None if res["ret_code"] else res["result"]


def closed_loss_profit(ticker, limit=1):
    res = SESSION.closed_profit_and_loss(symbol=ticker, limit=limit)
    return None if res["ret_code"] else res["result"]  # we have data array


def make_order(
    ticker,
    type,
    order_type="Market",
    price=0,
    qty=0,
    time_in_force="GoodTillCancel",
    stop_loss=0,
    take_profit=0,
):

    print(price, stop_loss, take_profit)
    print("price", "stop_loss", "take_profit")

    if order_type == "Market":
        res = SESSION.place_active_order(
            symbol=ticker,
            side=type,
            order_type=order_type,
            qty=qty,  # usd value
            time_in_force=time_in_force,
        )
    elif order_type == "Limit":
        res = SESSION.place_active_order(
            symbol=ticker,
            side=type,
            order_type=order_type,
            qty=qty,  # usd value
            time_in_force=time_in_force,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    return None if res["ret_code"] else res["result"]


def get_wallet(coin="BTC"):
    res = SESSION.get_wallet_balance(coin=coin)
    return None if res["ret_code"] else res["result"]


def query_active_order(ticker, order_id):
    res = SESSION.query_active_order(symbol=ticker, order_id=order_id)
    return None if res["ret_code"] else res["result"]


def cancell_all_active_orders(ticker):
    res = SESSION.cancel_all_active_orders(symbol=ticker)
    return None if res["ret_code"] else res["result"]


def set_stop(ticker, stop_loss, take_profit):
    res = SESSION.set_trading_stop(
        symbol=ticker, stop_loss=stop_loss, take_profit=take_profit
    )
    return None if res["ret_code"] else res["result"]
