from tensorflow.keras.layers import LSTM
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

from stock_prediction import create_model, load_data
from parameters import *


class Model:
    def __init__(self):
        self.test_df = self.final_df = None
        self.data = load_data(
            ticker,
            N_STEPS,
            scale=SCALE,
            split_by_date=SPLIT_BY_DATE,
            shuffle=SHUFFLE,
            lookup_step=LOOKUP_STEP,
            test_size=TEST_SIZE,
            feature_columns=FEATURE_COLUMNS,
        )
        # construct the model
        self.model = create_model(
            N_STEPS,
            len(FEATURE_COLUMNS),
            loss=LOSS,
            units=UNITS,
            cell=CELL,
            n_layers=N_LAYERS,
            dropout=DROPOUT,
            optimizer=OPTIMIZER,
            bidirectional=BIDIRECTIONAL,
        )

    def create_dirs(self):
        # create these folders if they does not exist
        if not os.path.isdir("results"):
            os.mkdir("results")

        if not os.path.isdir("logs"):
            os.mkdir("logs")

        if not os.path.isdir("data"):
            os.mkdir("data")

    def plot(self):
        """
        This function plots true close price along with predicted close price
        with blue and red colors respectively
        """
        plt.plot(self.test_df[f"true_adjclose_{LOOKUP_STEP}"], c="b")
        plt.plot(self.test_df[f"adjclose_{LOOKUP_STEP}"], c="r")
        plt.xlabel("Days")
        plt.ylabel("Price")
        plt.legend(["Actual Price", "Predicted Price"])
        plt.show()

    def get_final_df(self):
        """
        This function takes the `model` and `data` dict to
        construct a final dataframe that includes the features along
        with true and predicted prices of the testing dataset
        """

        X_test = self.data["X_test"]
        y_test = self.data["y_test"]

        # perform prediction and get prices
        y_pred = self.model.predict(X_test)

        if SCALE:
            y_test = np.squeeze(
                self.data["column_scaler"]["Close"].inverse_transform(
                    np.expand_dims(y_test, axis=0)
                )
            )
            y_pred = np.squeeze(
                self.data["column_scaler"]["Close"].inverse_transform(y_pred)
            )

        self.test_df = self.data["test_df"]
        # add predicted future prices to the dataframe
        self.test_df[f"adjclose_{LOOKUP_STEP}"] = y_pred
        # add true future prices to the dataframe
        self.test_df[f"true_adjclose_{LOOKUP_STEP}"] = y_test

        # sort the dataframe by date
        self.test_df.sort_index(inplace=True)
        self.final_df = self.test_df

    def predict(self):
        # retrieve the last sequence from data
        last_sequence = self.data["last_sequence"][-N_STEPS:]
        # expand dimension
        last_sequence = np.expand_dims(last_sequence, axis=0)
        # get the prediction (scaled from 0 to 1)
        prediction = self.model.predict(last_sequence)
        # get the price (by inverting the scaling)
        if SCALE:
            predicted_price = self.data["column_scaler"]["Close"].inverse_transform(
                prediction
            )[0][0]
        else:
            predicted_price = prediction[0][0]
        return predicted_price

    def train(self):
        self.create_dirs()

        # save the dataframe
        self.data["df"].to_csv(ticker_data_filename)

        # some tensorflow callbacks
        checkpointer = ModelCheckpoint(
            os.path.join("results", model_name + ".h5"),
            save_weights_only=True,
            save_best_only=True,
            verbose=1,
        )
        tensorboard = TensorBoard(log_dir=os.path.join("logs", model_name))

        # train the model and save the weights whenever we see
        # a new optimal model using ModelCheckpoint
        history = self.model.fit(
            self.data["X_train"],
            self.data["y_train"],
            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            validation_data=(self.data["X_test"], self.data["y_test"]),
            callbacks=[checkpointer, tensorboard],
            verbose=1,
        )

        # save the entire model to a file
        self.model.save("eth-usd_model.h5")

    def test(self):
        # load optimal model weights from results folder
        model_path = os.path.join("results", model_name) + ".h5"
        self.model.load_weights(model_path)

        # evaluate the model
        loss, mae = self.model.evaluate(
            self.data["X_test"], self.data["y_test"], verbose=0
        )

        # calculate the mean absolute error (inverse scaling)
        if SCALE:
            mean_absolute_error = self.data["column_scaler"]["Close"].inverse_transform(
                [[mae]]
            )[0][0]
        else:
            mean_absolute_error = mae

        # get the final dataframe for the testing set
        self.get_final_df()

        # predict the future price
        future_price = self.predict()

        # printing metrics
        print(f"Future price after {LOOKUP_STEP} days is {future_price:.2f}$")
        print(f"{LOSS} loss:", loss)
        print("Mean Absolute Error:", mean_absolute_error)

        # plot results
        self.plot()

        # print(final_df.tail(10))
        # save the final dataframe to csv-results folder
        results_folder = "model_results"
        if not os.path.isdir(results_folder):
            os.mkdir(results_folder)
        csv_filename = os.path.join(results_folder, "results.csv")
        self.final_df.to_csv(csv_filename)
        accuracy = 100 - (100 * (abs(self.test_df[f"true_adjclose_{LOOKUP_STEP}"] - self.test_df[f"adjclose_{LOOKUP_STEP}"]) / self.test_df[f"true_adjclose_{LOOKUP_STEP}"])).mean()
        print("accuracy of the model ", accuracy, "%")

        today = datetime.datetime.now()
        start = today - datetime.timedelta(days=59)  # 60 -1
        end = today - datetime.timedelta(days=29)

        data = f"""
        {accuracy}
        {start.strftime("%Y-%m-%d")} - {end.strftime("%Y-%m-%d")},
        """

        with open( os.path.join(results_folder, "results.txt"), "w") as f:
            f.write(data)


def main():
    model = Model()
    model.train()
    model.test()


if __name__ == "__main__":
    main()
