import sqlite3
import json

Alerts = {}

conn = sqlite3.connect("settings.db")
cursor = conn.cursor()

from enum import Enum
class Character(Enum):
    OwnCurrency = "OwnCurrency"
    all = "*"

# Создание таблицы
cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                   user_id INTEGER, 
                   OwnCurrency TEXT,
                   subscription INTEGER);
               """)

conn.commit()

conn.close()

def CreateBase(user_id):
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO settings VALUES(?);", (str(user_id), 'None'))
    conn.commit()

    conn.close()

def InsertToBase(user_id, OwnCurrency = 'None'):
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()

    Delete(user_id)

    cursor.execute("INSERT INTO settings VALUES(?, ?);", (str(user_id), str(OwnCurrency)))
    conn.commit()

    conn.close()

def Delete(user_id):
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM settings WHERE user_id = ?", (user_id,))
    conn.commit()

    conn.close()

def IsInBase(user_id, Character):
    isInBase = False
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()

    sql_select_query = f"""select {Character} from settings where user_id = ?"""
    cursor.execute(sql_select_query, (user_id,))
    records = cursor.fetchall()

    if Character in records:
        isInBase = True

    cursor.close()
    return isInBase

def GetFromBase(user_id, Character):
    if not IsInBase(user_id, user_id):
        InsertToBase(user_id)
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()

        sql_select_query = f"""select {Character} from settings where user_id = ?"""
        cursor.execute(sql_select_query, (user_id,))
        records = cursor.fetchone()

        cursor.close()
        return records
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if conn:
            conn.close()

def saveArray(filename, dict):
    with open(filename, 'w') as f:
        # indent=2 is not needed but makes the file more
        # human-readable for more complicated data
        json.dump(dict, f, indent=2)
    print("Saved successfully!")

def loadArray(filename):
    with open(filename, 'r') as f:
        return json.load(f)
    print("Load successfully!")