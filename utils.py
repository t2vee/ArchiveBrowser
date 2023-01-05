import json
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
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def critical(message):
        print(
            "LOG_LEVEL: [DEBUG] LOG_TYPE [CRITICAL] "
            + f"{bcolors.FAIL}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def warning(message):
        print(
            "LOG_LEVEL: [DEBUG] LOG_TYPE [WARNING] "
            + f"{bcolors.WARNING}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def info(message):
        print(
            "LOG_LEVEL: [DEBUG] LOG_TYPE [INFO] "
            + f"{bcolors.OKGREEN}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def instruction(message):
        print(
            "LOG_LEVEL: [DEBUG] LOG_TYPE [INSTRUCTION] "
            + f"{bcolors.UNDERLINE}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def dev(message):
        print(
            "LOG_LEVEL: [DEBUG] LOG_TYPE [DEVELOPMENT] "
            + f"{bcolors.BOLD}{message}{bcolors.ENDC}"
        )


try:
    cur.execute("CREATE TABLE pair(key TEXT UNIQUE, time TEXT)")
    cur.execute(
        "CREATE TABLE git(git_endpoint TEXT, user_repo TEXT UNIQUE, monitored TEXT, update_interval INTEGER, "
        "clone_data TEXT) "
    )
    cur.execute(
        "CREATE TABLE mirrors(name TEXT UNIQUE, source TEXT, update_interval TEXT)"
    )
except sqlite3.OperationalError as e:
    pass


class SqlKeysManagement:
    def __init__(self):
        pass

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
        pass

    async def grab_usr(self, key: str):
        res = cur.execute("SELECT * FROM pair WHERE key = '%s'" % (key))
        result = res.fetchall()
        if result is None:
            return {"code": 5001}
        return result


class AdministratorPanelDB:
    def __init__(self):
        pass

    @staticmethod
    async def get_git_repos():
        res = cur.execute("SELECT * FROM git")
        result = res.fetchall()
        data = json.dumps(result)
        if result is None:
            return {"code": 5001}
        return data

    @staticmethod
    async def get_git_repo_info(git_endpoint: str):
        res = cur.execute("SELECT * FROM git WHERE git_endpoint = '%s'" % (git_endpoint))
        result = res.fetchall()
        if result is None:
            return {"code": 5001}
        return result

    @staticmethod
    async def create_new_git_instance(repo_data):
        cur.execute(
            "INSERT INTO git VALUES ('%s', '%s', '%s', '%s', '%s')"
            % (
                repo_data[0],
                repo_data[1],
                repo_data[2],
                repo_data[3],
                repo_data[4],
            )
        )
        con.commit()
        return "repo added"

    @staticmethod
    async def delete_git_repo(git_endpoint):
        res = cur.execute("SELECT * FROM git WHERE git_endpoint = '%s'" % (git_endpoint))
        result = res.fetchone()
        if result is None:
            return {"code": 500, "error": "Entry does not exist"}
        try:
            cur.execute("DELETE FROM git WHERE git_endpoint = '%s'" % (git_endpoint))
            con.commit()
        except:
            return {"code": 500, "error": "Failed to delete sql entry"}
        return {"message": "The specified key and its data was successfully deleted."}


def loaded():
    # cur.execute("DELETE FROM git")
    # cur.execute(
    #    "INSERT INTO git VALUES ('%s', '%s', '%s', '%s', '%s')"
    #    % ("t2v/MirrorManager", "https://ttea.dev/t2v/MirrorManager.git", 1, 48, 'yes')
    # )
    # cur.execute(
    #    "INSERT INTO git VALUES ('%s', '%s', '%s', '%s', '%s')"
    #    % ("linustorvads/linux", "https://github.com/linustorvads/linux.git", 1, 4, 'yes')
    # )
    # con.commit()
    print("LOG:      (utils.py) - Program Utilities Loaded")
