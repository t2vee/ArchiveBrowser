import math
import sqlite3
import hashlib
import time
import uuid
import os
from datetime import datetime

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


now = datetime.now()
dt = now.strftime("%d/%m/%Y %H:%M:%S")


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def testing(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.OKCYAN}TEST{bcolors.ENDC}] "
            + f"{bcolors.OKCYAN}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def critical(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.FAIL}CRITICAL{bcolors.ENDC}] "
            + f"{bcolors.FAIL}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def warning(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] "
            + f"{bcolors.WARNING}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def info(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.OKGREEN}INFO{bcolors.ENDC}] "
            + f"{bcolors.OKGREEN}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def success(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.OKGREEN}SUCCESS{bcolors.ENDC}] "
            + f"{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.OKGREEN}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def fail(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.FAIL}FAIL{bcolors.ENDC}] "
            + f"{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.FAIL}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def warn(message):
        print(
            f"{dt}: [MM_LOG] LOG_TYPE: "
            + f"[{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.WARNING}WARN{bcolors.ENDC}] "
            + f"{bcolors.BOLD}{bcolors.UNDERLINE}{bcolors.WARNING}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def instruction(message):
        print(
            "LOG_LEVEL: [MM_LOG] LOG_TYPE: [INSTRUCTION] "
            + f"{bcolors.UNDERLINE}{message}{bcolors.ENDC}"
        )

    @staticmethod
    def dev(message):
        print(
            "LOG_LEVEL: [MM_LOG] LOG_TYPE: [DEVELOPMENT] "
            + f"{bcolors.BOLD}{message}{bcolors.ENDC}"
        )


try:
    cur.execute("CREATE TABLE pair(key TEXT UNIQUE, create_time TEXT)")
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


async def grab_sha256(file_path, filename):
    sha_file_structure = f"{os.environ.get('ROOT_PATH')}{file_path}/MM_DONT_INCLUDE-SHA256-{filename}.txt"
    if os.path.isfile(sha_file_structure):
        return await check_sha256(file_path, filename)
    with open(sha_file_structure, "w") as f:
        f.write(hashlib.sha256(file_path.encode("UTF-8")).hexdigest())
        return "Hash generated, Reload page to view"


async def check_sha256(file_path, filename):
    sha_file_structure = f"{os.environ.get('ROOT_PATH')}{file_path}/MM_DONT_INCLUDE-SHA256-{filename}.txt"
    with open(sha_file_structure, "r") as f:
        file_hash = f.readline()
        return file_hash


from functools import lru_cache


@lru_cache(maxsize=os.environ.get("QUERY_CACHE_AMOUNT"))
def find_files(filename, search_path):
    result = []
    filename_lower = filename.lower()  # Convert to lower case once
    for root, dir, files in os.walk(search_path):
        for file in files:
            if filename_lower == file.lower():
                result.append(os.path.join(root, file))
    return result


def loaded():
    print("LOG:      (utils.py) - Program Utilities Loaded")
