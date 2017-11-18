import sqlite3
import argparse


def addcurrency(conn, currency):
    """ add a list of currency strings to be added to database"""

    cur = conn.cursor()

    for c in currency:
        print(c)
        cur.execute('INSERT INTO currencies(name) VALUES (?)', (c, ))

    conn.commit()


def createtables(conn):
    
    # Connecting to the database file
    c = conn.cursor()

    # Creating a new SQLite table with 1 column
    c.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY ASC,\
                                                    date_open DATETIME,\
                                                    date_close DATETIME,\
                                                    price_open DOUBLE,\
                                                    price_close DOUBLE,\
                                                    symbol VARCHAR(10),\
                                                    volume INT,\
                                                    stop_orig DOUBLE,\
                                                    tp_orig DOUBLE,\
                                                    currency_id INT)')

    c.execute('CREATE TABLE IF NOT EXISTS currencies (id INTEGER PRIMARY KEY ASC,\
                                                    name VARCHAR(10))')

    c.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY,\
                                    date_open DATETIME,\
                                    date_close DATETIME)')

    c.execute('CREATE TABLE IF NOT EXISTS strategies (id INTEGER PRIMARY KEY,\
                                    date_open DATETIME,\
                                    date_close DATETIME)')
    
    conn.commit()

def parse_args():
    
    parser = argparse.ArgumentParser(description='Simple RAST db builder')

    parser.add_argument('-d','--dbname', action='store_true',default='../data/rast.db',required=False,help='Name of database to be created / altered')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    conn = sqlite3.connect(args.dbname)

    createtables(conn)
    addcurrency(conn, ['USD','CAD','EUR','JPY','AUD','CHF','NZD','GBP'])

    conn.close()


if __name__ == '__main__':
    main()