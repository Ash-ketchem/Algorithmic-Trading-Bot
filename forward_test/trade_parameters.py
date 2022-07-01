import datetime

today = datetime.datetime.now()

"""
    Parameters for the Trade class to take trades
"""

params = {
    "ticker": "ETHUSD",
    "yf_ticker": "ETH-USD",
    "time_frame": 5,  # interval 1m, 5m,
    "time_period": 200,  # no.of candles
    "sl": 0.4,
    "tp": 0.5,  # 0.05
    "max_trades_in_a_day": 5,
    "indicators_used": ["ema", "momentum"],
    "startegy_name": "3_ema_cross",
    "description": None,
    "ema_list": [9, 21, 55],
    "yf_time_interval": "5m",
    "training_period": {
        "start": today - datetime.timedelta(days=59),
        "end": today - datetime.timedelta(days=29),
    },
}
