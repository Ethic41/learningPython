# Author: Dahir Muhammad Dahir
# Date: 20th-03-2019


import mysql.connector as mysqlconn


class MakeConnection:
    def __init__(self): # constructor
        self.connection = mysqlconn.connect(host="127.0.0.1", user="root", passwd="phaux3070mysql$", database="bank_db")
        self.mycursor = self.connection.cursor()