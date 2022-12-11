import sqlite3
import time
import uuid

con = sqlite3.connect(r"db.sqlite", check_same_thread=False)
cur = con.cursor()
try:
    cur.execute("CREATE TABLE pair(key TEXT UNIQUE, time TEXT)")
except sqlite3.OperationalError as e:
    pass


async def get(key: str):
    res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
    result = res.fetchall()
    if result is None:
        return {"code": 5001}
    return result


async def create():
    key = uuid.uuid1()
    cur.execute("INSERT INTO pair VALUES ('%s', '%s')" % (str(key), time.time()))
    con.commit()
    return {str(key)}


async def delete(key):
    res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
    result = res.fetchone()
    if result is None:
        return {"code": 5003}
    cur.execute("DELETE FROM pair WHERE key = '%s'" % (key))
    con.commit()
    return {"message": "The specified key and its data was successfully deleted."}
