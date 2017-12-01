#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import time
import sqlite3


# File which contains "existing" database ...
database_file = './project.db'
schema_file = './data_wrangling_schema.sql'
csv2table = '../csv2sqlite/csv2sqlite.py'
csv_files = ['nodes.csv',
             'nodes_tags.csv',
             'ways.csv',
             'ways_nodes.csv',
             'ways_tags.csv']


# Function 2 show time and messages ...
def f_log(*args):
    local_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print("[{}]:").format(local_time),
    print(' ').join(args)


def remove_database():
    f_log("Checking if database",
          database_file,
          "exists ...")
    # Remove database file ...
    try:
        os.remove(database_file)
        f_log("Database",
              database_file,
              "removed ...")
    except OSError:
        pass
        f_log("Database",
              database_file,
              "does not exist ...")


def create_schema():
    f_log("Creating schema by",
          schema_file,
          "...")
    try:
        db = sqlite3.connect(database_file)
        cursor = db.cursor()
        query = open(schema_file, 'r').read()
        cursor.executescript(query)
        db.commit()
    except Exception as e:
        # Roll back any change if something goes wrong
        db.rollback()
        raise e
    finally:
        # Close the db connection
        db.close()


def load_csvs():
    f_log("Loading csv files ...")
    for csv_file in csv_files:
        f_log("Loading csv file",
              csv_file,
              "...")
        command = 'python {} {} {} {}'.format(csv2table,
                                              csv_file,
                                              database_file,
                                              csv_file[:-4])
        f_log("Executing",
              command,
              "...")
        return_value = os.system(command)
        if return_value == 0:
            f_log("Command",
                  command,
                  "ended ok ...")
        else:
            f_log("Error executing",
                  command,
                  "...")
    f_log("End of load_csvs() ...")


if __name__ == "__main__":
    remove_database()
    create_schema()
    load_csvs()
