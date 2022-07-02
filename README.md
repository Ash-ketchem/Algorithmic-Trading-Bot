# Algorithmic-Trading-Bot

The project aims at creating a trading system, named “Plutus”, that uses both technical analysis and neural networks for taking trading decisions effectively. 

This trading system can Backtest a strategy, train and use a neural network model and perform live trades on a trading/paper trading account. The trading bot can send messages to telegram groups as given by the user. A live dashboard is also used to monitor performance of the system.


The objective of this project is not to create the best trading system but to incorporate neural networks into traditional algorithmic trading and to understand whether neural networks are really efficient in algorithmic trading systems.


 USAGE
 
+______+

cd "TO FOLDER"

pip install -r requirements.txt


# To train and test a model
  1. cd model
  2. python3 model.py
  
 
# To backtest the strategy
  1. cd backtest
  2. python3 backtest_with_model.py

# To forward test the strategy
  1. cd forward_test
  2. python3 trade.py
 
# To use the live dashboard
  1. cd dashboard
  2. python3 app.py
  

