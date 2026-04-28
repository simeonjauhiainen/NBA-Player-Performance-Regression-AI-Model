import mysql.connector
from mysql.connector import Error
import pandas as pd
import requests



def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="prediction_modeldb"
        )
        print(conn)
        return conn

    except Error as e:
        print("Connection failed:", e)
        return None

