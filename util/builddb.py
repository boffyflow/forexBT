import sqlite3
import argparse
import pandas as pd


def createtables(conn):

    # Connecting to the database file

    cur = conn.cursor()

    # Create the tables

    cur.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY ASC,\
                                                    date_open DATETIME,\
                                                    date_close DATETIME,\
                                                    price_open DOUBLE,\
                                                    price_close DOUBLE,\
                                                    symbol VARCHAR(10),\
                                                    volume INT,\
                                                    stop_orig DOUBLE,\
                                                    tp_orig DOUBLE,\
                                                    currency_id INT,\
                                                    open_type_id INT,\
                                                    close_type_id INT)')

    cur.execute('CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY ASC,\
                                                    name VARCHAR(10),\
                                                    UNIQUE(name))')

    cur.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY,\
                                    date_open DATETIME,\
                                    date_close DATETIME)')

    cur.execute('CREATE TABLE IF NOT EXISTS strategies (id INTEGER PRIMARY KEY,\
                                    date_open DATETIME,\
                                    date_close DATETIME)')

    cur.execute('CREATE TABLE IF NOT EXISTS ordertypes (id INTEGER PRIMARY KEY,\
                                    name VARCHAR(32))')

    conn.commit()

    # adding reasonable default entries to the tables

    currencies = ['USD', 'CAD', 'EUR', 'JPY', 'AUD', 'CHF', 'NZD', 'GBP']
    for c in currencies:
        cur.execute('INSERT INTO currencies(name) VALUES (?)', (c, ))

    otypes = ['buy_limit', 'sell_limit', 'buy_market', 'sell_market', 'buy_stop', 'sell_stop']
    for o in otypes:
        cur.execute('INSERT INTO ordertypes(name) VALUES (?)', (o, ))

    conn.commit()

def parse_args():
    
    parser = argparse.ArgumentParser(description='Simple RAST db builder')

    parser.add_argument('-d','--dbname', action='store_true',default='../data/rast.db',required=False,help='Name of database to be created / altered')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    conn = sqlite3.connect(args.dbname)

#    createtables(conn)

    # print out table test
    df = pd.read_sql_query("SELECT * from currencies", conn)

    # verify that result of SQL query is stored in the dataframe
    print(df)

    conn.close()


if __name__ == '__main__':
    main()