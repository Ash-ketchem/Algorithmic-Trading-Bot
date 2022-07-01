import yfinance as yf
import datetime
from .ema_3cross import ThreeEma

"""
BacktestModel class is used to backtest the `3 ema trading strategy`

The test is done within a fixed time period using a LSTM Model for price prediction
combined with an algorithmatic trading strategy.

The run method initailizes the ThreeEma class and runs the backtest.

"""
class BacktestModel:
    def __init__(self, start, end, model_name):
        self.start = start
        self.end = end
        self.model_name = model_name

    def run(self, use_model=True):
        strategy = ThreeEma(use_model)
        strategy.indicators()
        strategy.model_set_up(self.model_name)
        strategy.strategy()
        strategy.test()
        strategy.results()


def main():
    model_name = "looser_50_20_5l_500.h5"
    today = datetime.datetime.now()
    start = today - datetime.timedelta(days=59)  # 60 -1   last 60 days
    end   = today - datetime.timedelta(days=29)  # first 30 days
    t = BacktestModel(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), model_name=f"backtest/{model_name}")
    t.run(use_model=True)

if __name__ == "__main__":
    main()
