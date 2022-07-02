from backtest import backtest_with_model as backtest
from forward_test import trade
from subprocess import Popen


def plutus():
    # backtest.main()
    trade.main()
    #linux
    Popen("python3 dashboard/app.py&", shell=True)


if __name__ == "__main__":
    plutus()
