# from pybit import HTTP
from pybit.inverse_perpetual import HTTP


API_NAME= "API_NAME"
API_SECRET = "API SECRET"
API_KEY = "API KEY"
BASE_ENDPOINT = "https://api-testnet.bybit.com"
SESSION = HTTP(BASE_ENDPOINT, api_key=API_KEY, api_secret=API_SECRET )



def get_position(ticker):
    res = SESSION.my_position(symbol=ticker)
    return None if res["ret_code"] else {
    "Side" : res["result"]["side"],
    "Position value" : res["result"]["position_value"],
    "Entry price" : res["result"]["entry_price"],
    "Leverage" : res["result"]["effective_leverage"],
    "Liquidation price" : res["result"]["liq_price"],
    "Take profit" : res["result"]["take_profit"],
    "Stop loss" : res["result"]["stop_loss"],
    "Wallet balance" : f'{res["result"]["wallet_balance"]} {ticker[:-3]}',
    }
