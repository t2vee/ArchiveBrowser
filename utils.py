import math
import sqlite3
import time
import uuid

con = sqlite3.connect(r"db.sqlite", check_same_thread=False)
cur = con.cursor()


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logger:
    def __init__(self):
        print('Logger Initialized')

    def critical(self, message="Empty Message. You shouldn't see this!"):
        print('LOG_LEVEL: [DEBUG] LOG_TYPE [CRITICAL] ' + f"{bcolors.FAIL}{message}{bcolors.ENDC}")

    def warning(self, message="Empty Message. You shouldn't see this!"):
        print('LOG_LEVEL: [DEBUG] LOG_TYPE [WARNING] ' + f"{bcolors.WARNING}{message}{bcolors.ENDC}")

    def info(self, message="Empty Message. You shouldn't see this!"):
        print('LOG_LEVEL: [DEBUG] LOG_TYPE [INFO] ' + f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")

    def instruction(self, message="Empty Message. You shouldn't see this!"):
        print('LOG_LEVEL: [DEBUG] LOG_TYPE [INSTRUCTION] ' + f"{bcolors.UNDERLINE}{message}{bcolors.ENDC}")

    def dev(self, message="Empty Message. You shouldn't see this!"):
        print('LOG_LEVEL: [DEBUG] LOG_TYPE [DEVELOPMENT] ' + f"{bcolors.BOLD}{message}{bcolors.ENDC}")


try:
    cur.execute("CREATE TABLE pair(key TEXT UNIQUE, time TEXT)")
    cur.execute("CREATE TABLE git(repo_name TEXT UNIQUE, repo_url TEXT, update_interval TEXT)")
    cur.execute("CREATE TABLE mirrors(name TEXT UNIQUE, source TEXT, update_interval TEXT)")
except sqlite3.OperationalError as e:
    pass


class SqlKeysManagement:
    def __init__(self):
        print('SqlKeysManagement Initialized')

    async def get(self, key: str):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchall()
        if result is None:
            return {"code": 5001}
        return result

    async def create(self):
        key = uuid.uuid1()
        cur.execute("INSERT INTO pair VALUES ('%s', '%s')" % (str(key), time.time()))
        con.commit()
        return {str(key)}

    async def delete(self, key):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchone()
        if result is None:
            return {"code": 5003}
        cur.execute("DELETE FROM pair WHERE key = '%s'" % (key))
        con.commit()
        return {"message": "The specified key and its data was successfully deleted."}


class AdministratorUserManagement:
    def __init__(self):
        print('AdministratorUserManagement Initialized')

    async def grab_usr(self, key: str):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchall()
        if result is None:
            return {"code": 5001}
        return result


class AdministratorPanelDB:
    def __init__(self):
        print('AdministratorPanelDB Initialized')

    async def get_git_repos(self, key: str):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchall()
        if result is None:
            return {"code": 5001}
        return result

    async def get_git_repo_info(self, key: str):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchall()
        if result is None:
            return {"code": 5001}
        return result

    async def clone_new_git_repo(self):
        key = uuid.uuid1()
        cur.execute("INSERT INTO pair VALUES ('%s', '%s')" % (str(key), time.time()))
        con.commit()
        return {str(key)}

    async def delete_git_repo(self, key):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchone()
        if result is None:
            return {"code": 5003}
        cur.execute("DELETE FROM pair WHERE key = '%s'" % (key))
        con.commit()
        return {"message": "The specified key and its data was successfully deleted."}

