from tensorflow.keras.layers import LSTM


"""
Parmetrs for the LSTM MODEL

"""

model_params = {
    "ticker": "ETH-USD",
    "period": "60d",
    "interval": "5m",
    "window_size": 50,
    "prediction_days": 1,
    "scale": True,
    "shuffle": True,
    "split_by_date": True,
    "test_size": 0.2,
    "feature_cols": ["Close", "Volume", "Open", "High", "Low"],
    "predicted_cols": "Close",
    "RNN_layers": 2,
    "cell": LSTM,
    "units": 256,
    "dropout": 0.4,
    "bidirectional": True,
    "loss": "mean_squared_error",
    "optimizer": "adam",
    "batch_size": 64,
    "epochs": 1,
    "model_name": "looser.h5",
    "compiled_model": None,
    "data": None,
    "results": {},
    "lookup_period": 20,
}
