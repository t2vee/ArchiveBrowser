import json
import math
import sqlite3
import hashlib
import time
import uuid
import git

import os
from urllib.parse import urlparse

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


async def find_files(filename, search_path):
    result = []
    for root, dir, files in os.walk(search_path):
        if str.lower(filename) in [x.lower() for x in files]:
            result.append(os.path.join(root, filename))
    return result


async def load_git_config():
    f = open("configs/git.json")
    config = json.load(f)
    for i in config:
        try:
            git_url = urlparse(i["info"]["url"])
            git.Repo.clone_from(
                i["info"]["url"],
                f"{os.environ.get('ROOT_PATH')}/GitStorage/{git_url.path.lstrip('/')}",
            )
        except:
            print(f'Initial Git clone failed. URI: {i["info"]["url"]}')
            pass
    f.close()
    return "temp"


def loaded():
    print("LOG:      (utils.py) - Program Utilities Loaded")
