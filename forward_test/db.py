import sqlite3

def db_setup():
    conn = sqlite3.connect("forward_test/trades.db")
    conn.execute("""create table if not exists trades
    (id integer primary key autoincrement, trade_type varchar(6), entry_price double, stop_loss double, take_profit double, exit_price double, closed_pnl double, result varchar(5))
    """)
    return conn
