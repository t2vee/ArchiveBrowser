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


def critical(message="Empty Message. You shouldn't see this!"):
    print('LOG_LEVEL: [DEBUG] LOG_TYPE [CRITICAL]' + f"{bcolors.FAIL}{message}{bcolors.ENDC}")


def warning(message="Empty Message. You shouldn't see this!"):
    print('LOG_LEVEL: [DEBUG] LOG_TYPE [WARNING]' + f"{bcolors.WARNING}{message}{bcolors.ENDC}")


def info(message="Empty Message. You shouldn't see this!"):
    print('LOG_LEVEL: [DEBUG] LOG_TYPE [INFO]' + f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")


def instruction(message="Empty Message. You shouldn't see this!"):
    print('LOG_LEVEL: [DEBUG] LOG_TYPE [INSTRUCTION]' + f"{bcolors.UNDERLINE}{message}{bcolors.ENDC}")


class Logger:
    def __init__(self, log_level):
        if log_level.lower() == 'debug':
            print(f"log level is set to {log_level}")
        #    def critical(message: str = "Empty Message. You shouldn't see this!"):
        #        print('LOG_LEVEL: [DEBUG] LOG_TYPE [CRITICAL]' + f"{bcolors.FAIL}{message}{bcolors.ENDC}")

        #    def warning(message: str = "Empty Message. You shouldn't see this!"):
        #        print('LOG_LEVEL: [DEBUG] LOG_TYPE [WARNING]' + f"{bcolors.WARNING}{message}{bcolors.ENDC}")

        #    def info(message: str = "Empty Message. You shouldn't see this!"):
        #        print('LOG_LEVEL: [DEBUG] LOG_TYPE [INFO]' + f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")

        #    def INSTRUCTION(message: str = "Empty Message. You shouldn't see this!"):
        #        print('LOG_LEVEL: [DEBUG] LOG_TYPE [INSTRUCTION]' + f"{bcolors.UNDERLINE}{message}{bcolors.ENDC}")
