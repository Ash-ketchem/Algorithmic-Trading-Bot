import sqlite3


def db_setup():
    conn = sqlite3.connect("backtest/backtest.db")
    conn.execute("""create table  if not exists backtest
    (id integer primary key autoincrement, trade_type varchar(6), entry_price double, exit_price double, result varchar(5))
    """)
    return conn
