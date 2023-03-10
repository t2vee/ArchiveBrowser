import sys
import shutil
import logging

# TODO Have a custom exception for tests
class RequiredTestFailed(Exception):
    print("A Required Test Failed. This must be fixed before continuing.")
    sys.exit()


class OptionalTestFailed(Exception):
    print("A test failed but it is not required for MirrorManager to run.")


# TODO Check disk space
async def disk_space_check():
    total, used, free = shutil.disk_usage("/")
    disk_space = [total // (2 ** 30), used // (2 ** 30), free // (2 ** 30)]
    if disk_space[3] < 20:
        raise RequiredTestFailed()
    elif disk_space[3] < 100:
        logging.warning("Although you have enough space for MirrorManager to run, It recommended that you allocate more")
    logging.info("test passed")


# TODO Check internet connection
async def network_check():
    r
# TODO Check if os is compatible
# TODO Check if jigdo is installed
# TODO Check mirrors.json is valid
# TODO Check system/cron scheduling if neither are present give option to select between internal or system
# TODO If one or more fixable tests fail give option to fix then repair
