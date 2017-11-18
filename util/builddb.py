import sqlite3
import argparse
 
 
def builddb(db_file):
    
    table_name1 = 'my_table_1'  # name of the table to be created
    table_name2 = 'my_table_2'  # name of the table to be created
    new_field = 'my_1st_column' # name of the column
    field_type = 'INTEGER'  # column data type

    # Connecting to the database file
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Creating a new SQLite table with 1 column
    c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=table_name1, nf=new_field, ft=field_type))

    # Creating a second table with 1 column and set it as PRIMARY KEY
    # note that PRIMARY KEY column must consist of unique values!
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=table_name2, nf=new_field, ft=field_type))

    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

def parse_args():
    
    parser = argparse.ArgumentParser(description='Simple RAST db builder')

    parser.add_argument('-d','--dbname', action='store_true',default='../data/rast.db',required=False,help='Name of database to be created / altered')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    builddb( args.dbname)

if __name__ == '__main__':
    main()