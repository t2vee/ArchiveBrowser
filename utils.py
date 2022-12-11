import math


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
