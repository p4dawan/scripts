# -*- coding: utf-8 -*-

from sqlite3 import connect
import os
import time

fecha = (time.strftime("%d-%m-%y"))

def sqlite_open_connection():

    try:
        if not os.path.isdir("db"):
            os.mkdir("db")
        db_path = os.path.join(os.path.dirname(__file__), fecha+"\\db\\info.db")
        db_path = os.path.join(db_path)
        connection = connect(db_path)
    except Exception as e:
        print(e)
        print("It has been an error establishing the connection with the database.")
        return None

    return connection

def sqlite_delete_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS ip")
    cursor.execute("DROP TABLE IF EXISTS banner")
    cursor.execute("DROP TABLE IF EXISTS dns")
    cursor.execute("DROP TABLE IF EXISTS whois")
    cursor.execute("DROP TABLE IF EXISTS domainName")
    cursor.execute("DROP TABLE IF EXISTS ports")


def sqlite_create_table():

    connection = sqlite_open_connection()
    if( connection != None ):
        try:
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS ip(id INTEGER PRIMARY "
                            + "KEY AUTOINCREMENT NOT NULL, ip VARCHAR(70))")
            cursor.execute("CREATE TABLE IF NOT EXISTS banner(bid INTEGER,"
                            + "id INTEGER, port INTEGER(5),cms VARHCAR(20),"
                            + "data VARCHAR(10000), screenshot LONGBLOB,"
                            + "PRIMARY KEY (bid),"
                            + "FOREIGN KEY (id) REFERENCES ip(id))")
        except Exception as e:
            print(e)
            print("[Error] It has been an error creating the tables.")
        finally:
            cursor.close()
            connection.close()

def sqlite_insert_data( ip, port, cms, banner, screenshot ):
    connection = sqlite_open_connection()

    if connection != None:
        try:
            with connection:
                cursor = connection.cursor()

                sql = "INSERT INTO ip(ip) VALUES (?)"
                cursor.execute( sql, ( str(ip), ) )
                iid = cursor.lastrowid

                sql = "INSERT INTO banner(id, port, cms, data, screenshot) VALUES (?, ?, ?, ?, ?)"
                cursor.execute( sql, ( int(iid), int(port),str(cms), str(banner), screenshot, ) )

            # Realizamos commit para guardar los cambios
            connection.commit()
        except Exception as e:
            print(e)
            print("It has been an error during the insertion.")
        finally:
            # Cerramos conexion
            cursor.close()
            connection.close()
