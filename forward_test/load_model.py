from tensorflow.keras.models import load_model

from .forwardTest_model import Model


class LoadModel:
    def __init__(self, full_data=True, df=None):
        self.model = Model()
        self.full_data = full_data
        self.df = df

    def data_setup(self, period=None):
        if type(self.df) != type(None):
            self.model.df = self.df.copy()
        elif period:
            self.model.get_data(period)
        self.model.clean_up()

    def train_model(self):
        self.model.create_model()
        self.model.train_model()

    def evaluate_model(self):
        self.model.evaluate_model(full_data=self.full_data)

    def load_old_model(self, model_name):
        self.model.model = load_model(model_name)

    def predict_next_day(self, df):
        return self.model.predict_tommorow(df)


"""

LoadModel class is designed to act as an interface
for the Trade class from trade.py to easily load a trained model.


This class is just a higher level abstrcation, to use
the functions of the `Model class` from forwardTest_model.py

"""
