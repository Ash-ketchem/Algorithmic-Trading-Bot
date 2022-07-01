import yfinance as yf

# import mplfinance as mpf
import numpy as np
import json
from subprocess import call
import pickle

# import from files
from .backtest import backtest
from .backtest_parameters import paramaters as bp
from .model_parameters import model_params as mp
from .load_model import LoadModel
from .telegram import TeleBot
from . import db


# To calculate momemtum of close prices of a given time period
def calculate_momentum(closes, n):
    s = 0

    for i in range(1, len(closes)):
        s += closes[i] - closes[i - 1]

    return s


class ThreeEma:
    def __init__(
        self,
        use_model=True,
    ):
        self.asset = bp["asset"]
        self.time_frame = bp["time_frame"]
        self.time_period = bp["time_period"]
        self.tp = bp["tp"]
        self.sl = bp["sl"]
        self.emas = bp["ema_list"]
        self.period = {
            "start": bp["training_period"]["start"].strftime("%Y-%m-%d"),
            "end": bp["training_period"]["end"].strftime("%Y-%m-%d"),
        }

        self.df = yf.download(
            self.asset, period=self.time_period, interval=self.time_frame
        )
        self.training_df = yf.download(
            self.asset,
            start=self.period["start"],
            end=self.period["end"],
            interval=self.time_frame,
        )

        self.df["Date"] = self.df.index.strftime("%d:%m:%y")
        self.training_df["Date"] = self.training_df.index.strftime("%d:%m:%y")

        # Algorithmatic conditions for trade entries

        self.short_crossover_med = False
        self.med_crossover_long = False

        self.short_crossunder_med = False
        self.med_crossunder_long = False

        self.profits, self.losses, self.break_evens = [], [], []
        self.trades = []
        self.long_profits, self.long_losses, self.short_profits, self.short_losses = (
            [],
            [],
            [],
            [],
        )

        self.even = True
        self.full_win_trades = 0
        self.break_even_trades = 0
        self.max_winners_in_a_row = 0
        self.max_losers_in_a_row = 0
        self.max_trades_in_a_day = bp["max_trades"]

        self.prediction_model = LoadModel(full_data=True, df=self.training_df.copy())
        self.min_threshold = 0.4
        self.df_len = len(self.df)
        self.future_prices = []
        self.threshold = 4.5

        self.use_model = use_model
        self.tele_bot = TeleBot()
        self.backtest_results = {}
        self.dashbrd_path = "backtest/"

    def indicators(self):
        self.df[f"short_ema"] = self.df["Close"].ewm(span=self.emas[0]).mean()
        self.df[f"med_ema"] = self.df["Close"].ewm(span=self.emas[1]).mean()
        self.df[f"long_ema"] = self.df["Close"].ewm(span=self.emas[2]).mean()
        self.df["Momentum"] = self.df["Close"].diff(
            10
        )  # ten period Momentum of asset close prices

    def check_conditions(self, index):

        if (
            self.df["short_ema"][index] > self.df["med_ema"][index]
            and self.df["short_ema"][index - 1] <= self.df["med_ema"][index - 1]
        ):
            self.short_crossover_med = True

        if (
            self.df["med_ema"][index] > self.df["long_ema"][index]
            and self.df["med_ema"][index - 1] <= self.df["long_ema"][index - 1]
        ):
            self.med_crossover_long = True

        if (
            self.df["short_ema"][index] < self.df["med_ema"][index]
            and self.df["short_ema"][index - 1] >= self.df["med_ema"][index - 1]
        ):
            self.short_crossunder_med = True

        if (
            self.df["med_ema"][index] < self.df["long_ema"][index]
            and self.df["med_ema"][index - 1] >= self.df["long_ema"][index - 1]
        ):
            self.med_crossunder_long = True

    def check_future(self, trade_type, index):
        signal = False

        if not self.use_model:
            return (
                True  # [ To test backtest performance without the use of the model!! ]
            )

        if (
            index - mp.get("window_size") - 1 < 0
        ):  # if there are not enough previous candlles to predict future, then return False
            return False

        if index + mp.get("window_size") - 1 > len(
            self.df
        ):  # if future index values exceeds the length of the df then return False
            return False

        # input(len(self.df[mp.get("feature_cols")][index - mp.get("window_size") + 1: index+1]))
        predicted_price = self.prediction_model.predict_next_day(
            self.df[mp.get("feature_cols")][
                index - mp.get("window_size") + 1 : index + 1
            ]
        )
        # print(f"[+] predicted price after {mp['lookup_period']} days is {predicted_price} ...")

        # if predicted price +/- some threshold value is favourable to the condition then only take the Trade
        if trade_type == "long":
            if (
                predicted_price + self.threshold > self.df["Close"][index]
                and predicted_price - self.threshold > self.df["Close"][index]
            ):
                signal = True

        if trade_type == "short":
            if (
                predicted_price - self.threshold < self.df["Close"][index]
                and predicted_price + self.threshold < self.df["Close"][index]
            ):
                signal = True

        # if trade_type == "long":
        #     if predicted_price  > self.df["Close"][index]:
        #         signal = True

        # if trade_type == "short":
        #     if predicted_price  < self.df["Close"][index]:
        #         signal = True

        print(
            f"""
        ======================================================================================================
        #
        |   Trade Type             : {trade_type}
        |   Signal Generated       : {signal}
        |   Original Future Price  : {round(self.df['Close'][index + mp.get("lookup_period") - 1], 3)}
        |   Predicted Future Price : {round(float(predicted_price), 3)}
        |   Current Close Price    : {round(self.df['Close'][index], 3)}
        #
        ======================================================================================================
        """
        )

        # call('clear')

        return signal

    def strategy(self):
        call("clear")  # clear the screen

        for i in range(1, len(self.df)):

            self.check_conditions(i)

            if self.short_crossover_med:
                if self.med_crossover_long and self.df["Momentum"][i] > 0:
                    # Using the model to confirm the signals generated
                    if self.check_future(trade_type="long", index=i):
                        self.trades.append(
                            {
                                "type": "long",
                                "bar_index": i if i == len(self.df) - 1 else i + 1,
                                "entry_price": self.df["Open"][i]
                                if i == len(self.df) - 1
                                else self.df["Open"][i + 1],
                            }
                        )
                    self.short_crossover_med = (
                        self.med_crossover_long
                    ) = False  # Resetting generated trade conditions

            elif self.short_crossunder_med:
                if self.med_crossunder_long and self.df["Momentum"][i] < 0:
                    # Using the model to confirm the signals generated
                    if self.check_future(trade_type="short", index=i):
                        self.trades.append(
                            {
                                "type": "short",
                                "bar_index": i if i == len(self.df) - 1 else i + 1,
                                "entry_price": self.df["Open"][i]
                                if i == len(self.df) - 1
                                else self.df["Open"][i + 1],
                            }
                        )
                    self.short_crossunder_med = (
                        self.med_crossunder_long
                    ) = False  # Resetting generated trade conditions

    def test(self):
        # backtest function is used to backtest the trades
        (
            self.max_winners_in_a_row,
            self.max_losers_in_a_row,
            self.break_evens,
        ) = backtest(
            self.df,
            len(self.df),
            self.trades,
            self.tp,
            self.sl,
            self.profits,
            self.losses,
            even=self.even,
        )
        for trade in self.profits:
            trade["result"] = "win"
        for trade in self.losses:
            trade["result"] = "loss"
        for trade in self.break_evens:
            trade["result"] = "even"

        self.trades = self.profits + self.losses + self.break_evens
        self.trades.sort(key=lambda t: t["bar_index"])

        # write to db

        conn = db.db_setup()
        for trade in self.trades:
            cursor = conn.cursor()
            query = "insert into backtest (trade_type, entry_price, exit_price, result) values (?,?,?,?)"
            params = (
                trade["type"],
                trade["entry_price"],
                trade["closing_price_close"],
                trade["result"],
            )
            cursor.execute(query, params)

        conn.commit()

        print("[*] Data sucessfully written to backtest.db..")

    def results(self):
        self.long_losses = [loss for loss in self.losses if loss["type"] == "long"]
        self.short_losses = [loss for loss in self.losses if loss["type"] == "short"]

        self.long_profits = [
            profit for profit in self.profits if profit["type"] == "long"
        ]
        self.short_profits = [
            profit for profit in self.profits if profit["type"] == "short"
        ]

        long_trades = len(self.long_profits) + len(self.long_losses)
        short_trades = len(self.short_profits) + len(self.short_losses)

        total_trades = len(self.trades)
        total_wins = len(self.profits)
        total_losses = len(self.losses)
        even_trades = len(self.break_evens)

        # win_rate = (total_wins / (total_wins + total_losses)) * 100
        win_rate = (total_wins / total_trades) * 100

        # win_rate_with_evens = (total_wins / (total_wins + total_losses)) * 100
        win_rate_with_evens = ((total_wins + even_trades) / total_trades) * 100

        self.backtest_results = {
            "asset": "ETHERIUM / USD",
            "time_frame": self.time_frame,
            "time_period": f"{self.period['start']} - {self.period['end']}",
            "total_trades": total_trades,
            "losers": total_losses,
            "winners": total_wins,
            "evens": even_trades,
            "win_rate": win_rate,
            "win_rate_with_even": round(win_rate_with_evens, 2),
        }

        msg = f"""
        + =================================================================================== +
        |
        |     General Info
        |  + -------------- +
        |
        |  ASSET           : {self.asset}
        |  STOP LOSS (%)   : {self.sl}
        |  TAKE PROFIT (%) : {self.tp}
        |
        |
        |     Backtest Results
        |  + ------------------ +
        |
        |   TOTAL TRADES : {total_trades}
        |   TOTAL WINS   : {total_wins - even_trades}
        |   TOTAL LOSSES : {total_losses}
        |   EVEN TRADES  : {even_trades}
        |
        |   WIN RATE (WITHOUT EVEN TRADES ) : {round(win_rate, 2)} %
        |   WIN RATE (WITH EVEN TRADES )    : {round(win_rate_with_evens, 2)} %
        |
        |   LONG TARDES  : {long_trades}
        |   SHORT TRADES : {short_trades}
        |
        |   LONG WINS    : {len(self.long_profits)}
        |   LONG LOSSES  : {len(self.long_losses)}
        |   SHORT WINS   : {len(self.short_profits)}
        |   SHORT LOSSES : {len(self.short_losses)}
        |
        |
        + =================================================================================== +
        """

        msg_telegrm = ""  # write the telegram message
        if self.tele_bot.send_msg(msg_telegrm):
            print(f"[+] {len(self.trades)} Trade message send to telegram group...")
        else:
            print(f"[-] Failed to send message...")

        with open("backtest/msg.txt", "w") as f:
            f.write(msg)

        self.save_data()

        with open("backtest/trades.txt", "w") as f:
            data = f"""
            Trades taken
            _____________

        {json.dumps(self.trades, indent=4)}

            details
            ___________

        Long Trades won:

        {json.dumps(self.long_profits, indent=4)}

        Short Trades Won:

        {json.dumps(self.short_profits, indent=4)}

        Even Trades:

        {json.dumps(self.break_evens, indent=4)}

        Long Trades lost:

        {json.dumps(self.long_losses, indent=4)}

        Short Trades lost:

        {json.dumps(self.short_losses, indent=4)}

            """

            f.write(data)
            print("[+] Backtest data written to file trades.txt...")

    def visualize(self):  # plotting results
        buys = [i["bar_index"] for i in self.trades if i["type"] == "long"]
        sells = [i["bar_index"] for i in self.trades if i["type"] == "short"]

        plt.figure(figsize=(12, 4))

        # plotting losses

        plt.scatter(
            self.df.iloc[self.long_losses].index,
            self.df.iloc[self.long_losses]["Close"],
            marker="v",
            color="green",
        )

        plt.scatter(
            self.df.iloc[self.short_losses].index,
            self.df.iloc[self.short_losses]["Close"],
            marker="v",
            color="red",
        )

        plt.plot(self.df["short_ema"], label="short_ema", color="Blue")
        plt.plot(self.df["med_ema"], label="med_ema", color="orange")
        plt.plot(self.df["long_ema"], label="long_ema", color="red")

        plt.legend()
        plt.show()

    """
        load an old model and populate the trading df with future prices
    """

    def model_set_up(self, model_name=""):
        # loading the model for backtesting
        if model_name:
            self.prediction_model.load_old_model(model_name=model_name)
            self.prediction_model.data_setup()
            print("[*] loaded model!!!\n")
        else:
            assert "[-] You have to pass a Model Name..."

    def intro(self):
        pass  # plutus

    def save_data(self):
        # pickling the backtest results
        with open(self.dashbrd_path + "backtest_results.txt", "wb") as f:
            pickle.dump(self.backtest_results, f)
