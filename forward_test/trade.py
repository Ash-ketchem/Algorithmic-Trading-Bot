import numpy as np
import json
import pandas as pd
from pybit import HTTP
import yfinance as yf
from subprocess import call

from .bybit_functions import *
from .trade_parameters import params as ps
from .model_parameters import model_params as mp
from .load_model import LoadModel
from .telegram import TeleBot
from .db import db_setup

"""
    Trade class is used to Forward Test or Trade in real with the strategy
    we used to backtest the assest.

    We get the last 5 days price(in real-time) data from yahoo finance and analyzes
    the data for trade opportunities.If all condions meet then the trade is taken
    in bybit exchange (currently using bybit testnet for deminstartion purposes).

    We use the bybit api to interface with the exchange in real-time for taking
    and closing trades.The class Trade monitiors the trades taken and and ensure
    that only one trade is taken per account.

    Telegram api is used to send messages to the user when trades are taken and
    closed.All Taken trades are stored in a database also.

"""
class Trade:

    def __init__(self, model_name, use_model=True):
        self.ticker = ps["ticker"]
        self.yf_ticker = ps["yf_ticker"]
        self.time_frame = ps["time_frame"]
        self.sl = ps["sl"]
        self.tp = ps["tp"]
        self.emas = ps["ema_list"]

        self.df = pd.DataFrame()
        self.short_crossover_med = False
        self.med_crossover_long = False
        self.short_crossunder_med = False
        self.short_crossunder_med = False

        self.trades, self.pending_trades, self.finished_trades = [], [], []
        self.profits, self.losses, self.evens = [], [], []
        self.prediction_model = None

        self.in_a_trade = False
        self.order_verified = False
        self.min_cutoff = 0.004

        self.last_trade_id = None
        self.model_name = model_name
        self.use_model = use_model
        self.tele_bot = TeleBot()
        self.last_trade_id = 0
        self.conn = db_setup() # database connection
        self.testing = False

    def get_data(self):
        print("[*] Fetching Asset Data...")
        self.df = yf.download(self.yf_ticker, interval=ps["yf_time_interval"], period="5d")

    def indicators(self):
        self.df["short_ema"] = self.df["Close"].ewm(span=self.emas[0]).mean()
        self.df["med_ema"] = self.df["Close"].ewm(span=self.emas[1]).mean()
        self.df["long_ema"] = self.df["Close"].ewm(span=self.emas[2]).mean()
        self.df["Momentum"] = self.df["Close"].diff(10)  # ten period Momentum indicator

    def check_conditions(self, index):

        if self.df["short_ema"][index] > self.df["med_ema"][index] and self.df["short_ema"][index-1] <=  self.df["med_ema"][index-1]:
            self.short_crossover_med = True

        if self.df["med_ema"][index] > self.df["long_ema"][index] and self.df["med_ema"][index-1] <=  self.df["long_ema"][index-1]:
            self.med_crossover_long = True


        if self.df["short_ema"][index] < self.df["med_ema"][index] and self.df["short_ema"][index-1] >=  self.df["med_ema"][index-1]:
            self.short_crossunder_med = True


        if self.df["med_ema"][index] < self.df["long_ema"][index] and self.df["med_ema"][index-1] >=  self.df["long_ema"][index-1]:
            self.med_crossunder_long = True

    def check_future(self, trade_type, index):
        signal = False

        if not self.use_model:  # use the model or not for deciding to take the trade
            return True

        if index - mp["lookup_period"] - 1 < 0 :
             return False

        predicted_price = self.prediction_model.predict_next_day(self.df[mp.get("feature_cols")][index - mp.get("lookup_period") + 1: index+1])
        print(f"[*] predicted price after {mp['lookup_period']} candles is {predicted_price}")

        if trade_type == "long":
            if predicted_price + 4.5 > self.df["Close"][index] and predicted_price - 4.5 > self.df["Close"][index]:
                signal = True

        if trade_type == "short":
            if predicted_price - 4.5 < self.df["Close"][index] and  predicted_price + 4.5 < self.df["Close"][index]:
                signal = True

        print(f"""
        ======================================================================================================
        #
        |   Trade Type             : {trade_type}
        |   Signal Generated       : {signal}
        |   Predicted Future Price : {round(float(predicted_price), 3)}
        |   Current Close Price    : {round(self.df['Close'][index], 3)}
        #
        ======================================================================================================
        """)

        return signal

    def model_setup(self):
        self.prediction_model = LoadModel(full_data=True)
        self.prediction_model.load_old_model(model_name=self.model_name)
        self.prediction_model.data_setup(period={
            "start": ps["training_period"]["start"].strftime("%Y-%m-%d"), "end": ps["training_period"]["end"].strftime("%Y-%m-%d")
        })
        print("[+] Loaded the Model...")

    def get_last_trade_id(self):
        res = closed_loss_profit(self.ticker)
        self.last_trade_id = res["data"][0]["id"]

    def strategy(self):
        """
            Fetch the real-time ticker price data and calculate the indicator.
            Get the second last candle data or candle index and check for entry signals
        """
        self.get_data()
        self.indicators()

        call("clear") # clear the terminal screen

        second_last_index = len(self.df) - 2
        self.check_conditions(second_last_index)

        if self.short_crossover_med:
            if self.med_crossover_long and self.df["Momentum"][second_last_index] > 0:
                if self.check_future(trade_type="long", index=second_last_index) : # model condition check
                    self.trades.append({
                        "type" : "long",
                        "bar_index" : second_last_index,
                        "entry_price" : None
                    })
                self.short_crossover_med = self.med_crossover_long = False

        if self.short_crossunder_med:
            if self.med_crossunder_long and self.df["Momentum"][second_last_index] < 0:
                if self.check_future(trade_type="short", index=second_last_index) : # model condition check
                    self.trades.append({
                        "type" : "short",
                        "bar_index" : second_last_index,
                        "entry_price" : None
                    })
                self.short_crossunder_med = self.med_crossunder_long = False

        if len(self.trades) == 1 or True: # Testing
            if self.check_future(trade_type="long", index=second_last_index) :
                self.trades.append({
                            "type" : "long",
                            "bar_index" : second_last_index,
                            "entry_price" : None
                        })
                self.trade_manager(order_type="Market")

    def trade_manager(self, order_type="Market"):

        """
            check if already in a trade else
            take the trade in the exchange and set stop loss and take profit prices
        """

        if self.in_a_trade:
            return

        entry_price = self.df["Close"].iloc[-2]
        trade_type = self.trades[0]["type"]
        side = "Buy" if self.trades[0]["type"] == "long" else "Sell"

        print("[*] taking the order...")

        if order_type == "Limit":
            entry_price = entry_price * (1 - self.min_cutoff / 100) if trade_type == "long" else entry_price * (1 + self.min_cutoff / 100) # cut0fff % of close price
            self.trades[0]["entry_price"] = round(entry_price, 2)
            self.trades[0]["take_profit"] = round(entry_price * (1 + self.tp / 100) if trade_type == "long" else  entry_price * (1 - self.tp / 100), 2)
            self.trades[0]["stop_loss"] = round(entry_price * (1 - self.sl / 100)  if trade_type == "long" else entry_price * (1 + self.sl / 100), 2)
            self.trades[0]["break_even"] = round(entry_price * (1 + self.sl / 100)  if trade_type == "long" else entry_price * (1 - self.sl / 100), 2)

            res = make_order(ticker=self.ticker,type=side, order_type=order_type, qty=100, price=self.trades[0]["entry_price"], stop_loss=self.trades[0]["stop_loss"], take_profit=self.trades[0]["take_profit"] )
            if not res:
                print("[-] Failed to make an order...")
            self.trades[0]["order_id"] = res["order_id"]

        elif order_type == "Market":
            res  = make_order(ticker=self.ticker, type=side, order_type=order_type, qty=100)

            if not res:
                print("error in taking order")
                # Do retry

            self.trades[0]["order_id"] = res["order_id"]

            res = query_active_order(self.ticker, res["order_id"])
            if not res:
                print("eror in taking order")

            entry_price = float(res["last_exec_price"])

            self.trades[0]["entry_price"] = entry_price
            self.trades[0]["stop_loss"] = round(entry_price * (1 - self.sl / 100)  if trade_type== "long" else entry_price * (1 + self.sl / 100), 2)
            self.trades[0]["take_profit"] = round(entry_price * (1 + self.tp / 100) if trade_type== "long" else  entry_price * (1 - self.tp / 100), 2)
            self.trades[0]["break_even"] = round(entry_price * (1 + self.sl / 100)  if trade_type== "long" else entry_price * (1 - self.sl / 100), 2)


            print("[*] setting stop loss and take profit...")
            res = set_stop(self.ticker, self.trades[0]["stop_loss"], self.trades[0]["take_profit"])

            if not res:
                print("[-] failed to set stoploss and take_profit...")
                # do retry
            else:
                print("[+] Sucessfully set stoploss and takeprofit...")

        if not self.trades[0].get("order_id"):
            self.in_a_trade = False
            assert "order placed or not can't be verified"

        self.order_verifier()

        if self.order_verified:
            # if order sucessful send a telegram message and add data to the db
            msg_telegrm = f"""
            Type : {self.trades[0]['type']}
            Entry Price : {self.trades[0]['entry_price']}
            Stop loss : {self.trades[0]['stop_loss']}
            Take profit : {self.trades[0]['take_profit']}
            """
            # return
            id = self.tele_bot.send_msg(msg_telegrm)
            if id:  # type(id) == int
                self.last_trade_id = id
                print(f"[+] {len(self.trades)} Trade message send to telegram group...")
            else:
                print(f"[-] Failed to send message...")

            cursor = self.conn.cursor()
            query = "insert into trades (trade_type, entry_price, stop_loss, take_profit, exit_price, closed_pnl, result) values (?,?,?,?,?,?,?)"
            params = ( self.trades[0]["type"], self.trades[0]["entry_price"], self.trades[0]["stop_loss"], self.trades[0]["take_profit"], 0, 0, "ongoing" )
            # inserting the data of the trade currently in as "reslut : ongoing"
            cursor.execute(query, params)
            self.conn.commit()

    def order_verifier(self):

        """
            Try maximum 5 times to verify the order in the exchange , else cancel all active orders
        """
        count = 5

        while count > 0:
            print("[*] Waiting till the order is filled...")

            res = query_active_order(self.ticker, self.trades[0]["order_id"])

            if not res:
                print("error trade order_verifier")
                return False
            else:
                if res["order_status"] != "Filled":
                    if len(self.pending_trades) >= 1:
                        self.pending_trades = []
                    self.pending_trades.append(self.trades[0])
                    self.trades = []
                    self.in_a_trade = False
                    self.order_verified = False
                    count -= 1
                    time.sleep(10)
                else:
                    print("[+] The order was Filled sucessfully...")
                    self.pending_trades = []
                    self.in_a_trade = True
                    self.order_verified = True
                    count = -5


            if count == 0:
                res = cancell_all_active_orders(self.ticker) # cancel all other limit orders
                if not res:
                    print("[-] failed to cancel active orders...")

    def trade_progress_check(self):

        """
            Check the progress of the trade using the api
            if trade is finished store the trade data
            and look for next oppurtunities.
        """

        print("[*] Checking Trade progress...")

        if not self.order_verified:
            print("[-] order not verified...")
            return

        trade_finished = False

        res = get_position(self.ticker)

        if res["side"] == "None":   # means last position was closed
            print("[*] Waiting 30 seconds till the position gets reflected in the exchange...")
            time.sleep(30)          # wait till the position gets reflected in the profit loss records
            res = closed_loss_profit("ETHUSD", limit=1)
            if not res:
                print('[*] some thing bad happened...')
                return "TRY_AGAIN"

            data = res["data"][0]

            if data["id"] == self.last_trade_id:
                print("[-] Please wait while the trade gets reflected on the exchange...")
                return "TRY_AGAIN"
            else:
                trade_finished = True
                self.in_a_trade = self.order_verified = False
                self.trades[0]["avg_entry_price"]  = data["avg_entry_price"]
                self.trades[0]["avg_exit_price"]  = data["avg_exit_price"]
                self.trades[0]["closed_pnl"]  = data["closed_pnl"]
                self.trades[0]["leverage"]  = data["leverage"]
                self.trades[0]["result"]  = "win" if data["closed_pnl"] > 0 else "lose"

                self.finished_trades.append(self.trades[0])
                self.get_last_trade_id()

                # write to db and a file

                cursor = self.conn.cursor()

                #deleting ongoing trade row
                query = "delete from trades where result = 'ongoing'"
                cursor.execute(query)

                query = "insert into trades (trade_type, entry_price, stop_loss, take_profit, exit_price, closed_pnl, result) values (?,?,?,?,?,?,?)"
                params = ( self.trades[0]["type"], self.trades[0]["avg_entry_price"], self.trades[0]["stop_loss"], self.trades[0]["take_profit"], self.trades[0]["avg_exit_price"], self.trades[0]["closed_pnl"], self.trades[0]["result"] )
                cursor.execute(query, params)
                self.conn.commit()

                print("[+] Trade Finished...")
                print(json.dumps(self.finished_trades[-1], indent=4))

                self.trades = []


        # trade_type = self.trades[0]["type"]
        # if trade_type == "long": normal paper trading method

    def run(self):
        self.get_last_trade_id()
        self.model_setup()

        while True:
            if self.in_a_trade:
                if self.trade_progress_check() == "TRY_AGAIN":
                    print("[-] Sleeping 30 seconds and will retry after that...")
                    time.sleep(30)
            else:
                self.strategy()
                # print(self.df.tail(5))

            print("[+] Sleeping for 5 minutes...")
            time.sleep(5)
            # time.sleep(60 * 5) # sleep 5 minutes


def main():
    model_name = "looser_500_5l.h5"
    bot  = Trade(model_name=f"forward_test/{model_name}", use_model=False)
    bot.run()


if __name__ == "__main__":
    main()
    pass
