import sqlite3
from sqlite3 import Error
import os.path
import pandas as pd 

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def select_all_records(conn,table_name):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param table_name: table name
    :return: rows of a table 
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table_name)

    rows = cur.fetchall()

    return rows

def update_processed_boat(conn,boat_link):
    """
    Update db for complete boat
    :param conn: the Connection object
    :param boat_link: the adverts link
    :return:
    """
    try:
        c = conn.cursor()
        c.execute("UPDATE adverts SET processed = 1 WHERE link = '" + boat_link + "'")
    except Error as e:
        print(e)

def get_boat_links_to_process(conn):
    """
    pull boats not processed 
    :param conn: the Connection object
    :return rows: the links to boat adverts  
    """
    try:
        c = conn.cursor()
        c.execute("SELECT DISTINCT link FROM adverts WHERE processed = 0 ")
        rows = c.fetchall()
        return rows

    except Error as e:
        print(e)

def main(database):
    
    sql_create_adverts_table = """ CREATE TABLE IF NOT EXISTS adverts (
                                        id integer PRIMARY KEY,
                                        link text NOT NULL,
                                        processed INT NOT NULL
                                    ); """

    sql_create_boats_spec_table = """ CREATE TABLE IF NOT EXISTS boats (
                                    id integer PRIMARY KEY,
                                    link text,
                                    price text,
                                    status text,
                                    desc text,
                                    specs text,
                                    dealer text,
                                    title text,
                                    location text
                                );"""


    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_adverts_table)

        # create tasks table
        create_table(conn, sql_create_boats_spec_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()