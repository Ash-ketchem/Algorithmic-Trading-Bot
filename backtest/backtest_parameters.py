import datetime

today =  datetime.datetime.now()

paramaters = {

    "asset" : "ETH-USD",
    "time_frame" : "5m",
    "time_period" : "30d",
    "tp" : 0.5,
    "sl" : 0.4,
    "ema_list" : [9, 21, 55], # [short_ema, med_ema, high_ema]
    "max_trades" : 5,
    "time_period_int" : 60,
    "feature_cols" :["Close"],
    "training_period" : {
        "start" : today - datetime.timedelta(days=59),
        "end" : today- datetime.timedelta(days=29)
        }
}


"""
    =========================================================================
    |                                                                       |
    | [*] Model Training period is first 30 days of last 60 days from today |                                                                            
    |                                                                       |
    =========================================================================
    |                                                                       |
    | [*] Backtesting period is last 30 days of last 60 days from today     |
    |                                                                       |
    =========================================================================

"""
