import numpy as np
import pandas as pd
import yfinance as yf
import time
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

from .model_parameters import model_params as mp


class Model:

    """ "

    Model class is an optimized version of the real Model class
    used while creating and training the LSTM MODEL.

    This class is optimized to work with the Trade class efficiently without
    wasting much time and resources while forawrd_testing the startegy.

    """

    def __init__(self):
        self.df = None
        self.model = None
        self.predicted_prices = None
        self.predicted_prices_train = None
        self.original_prices = None
        self.original_prices_train = None
        self.predicted_price = 0
        self.future_df = pd.DataFrame()
        self.saved_scaler = {}  # to save the scalers used while model was trained

        # to remove scientific notations from numpy arrays
        np.set_printoptions(suppress=True)

    def get_data(self, period):
        ticker = mp.get("ticker")
        self.df = yf.download(
            ticker,
            start=period["start"],
            end=period["end"],
            interval=mp.get("interval"),
        )

    def clean_up(self):
        # optmized version to replicate the original scalers used while training the model

        for col in mp["feature_cols"]:
            scaler = MinMaxScaler()
            full_data = np.expand_dims(self.df[col].values, axis=1)
            data_scaler = scaler.fit(full_data)
            self.saved_scaler[col] = data_scaler

    def predict_tommorow(self, lastn_df):  # function to preedict future price
        lastn_days = lastn_df.copy()

        for col in mp.get("feature_cols"):
            full_data = np.expand_dims(lastn_days[col].values, axis=1)
            lastn_days[col] = self.saved_scaler[col].transform(full_data)

        lastn_days = lastn_days[mp.get("feature_cols")].values

        lastn_days = lastn_days.reshape(
            1, mp.get("window_size"), len(mp.get("feature_cols"))
        )

        predicted_price_tmmrw = self.model.predict(lastn_days)
        predicted_price_tmmrw = self.saved_scaler[
            mp.get("predicted_cols")
        ].inverse_transform(predicted_price_tmmrw)

        return predicted_price_tmmrw[0][0]
