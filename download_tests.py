import os
import sys
import time
import json
import shutil
import socket
import asyncio
from utils import Logger

log = Logger()

#log.basicConfig(
#    level=log.INFO,
#    format="%(asctime)s [%(levelname)s] %(message)s",
#    handlers=[log.FileHandler("debug.log"), log.StreamHandler()],
#)


# Check disk space
async def disk_space_check():
    log.testing('Starting Disk Size Check...')
    total, used, free = shutil.disk_usage("/")
    disk_space = [total // (2**30), used // (2**30), free // (2**30)]
    if disk_space[2] < 20:
        log.critical(
            "This system has less than 20gb of storage. MirrorManager requires more space for smooth operation."
        )
        time.sleep(1)
        pass
        #raise RequiredTestFailed('Invalid Disk Size')
    elif disk_space[2] < 100:
        log.warning(
            "Although you have enough space for MirrorManager to run, It recommended that you allocate more"
        )
    log.success("Disk Space test passed")
    pass


# Check internet connection
async def is_connected():
    log.testing('Starting Network Connection Test...')
    pass_or_fail = []
    dns_servers = [
        "one.one.one.one",
        "8.8.8.8",
        "8.8.4.4",
        "1.0.0.1",
        "94.140.14.14",
        "94.140.15.15",
    ]
    for dns in dns_servers:
        try:
            log.testing("Pinging " + dns)
            host = socket.gethostbyname(dns)
            s = socket.create_connection((host, 80), 2)
            s.close()
            log.info(f'Connection to {dns} was successful')
            pass_or_fail.append(True)
            pass
        except Exception:
            log.critical(f"Ping check for {dns} failed")
            pass_or_fail.append(False)
            pass
        pass
    num_true = pass_or_fail.count(True)
    num_false = pass_or_fail.count(False)
    if num_true < num_false:
        log.critical("the internet connection test had too many failures")
        time.sleep(1)
        raise RequiredTestFailed('Network Connection Failure')
    log.success("Network test passed")
    pass


# Check if os is compatible
async def compatible_os():
    log.testing('Starting OS Compat Test...')
    if sys.platform.startswith("freebsd"):
        log.info("Freebsd as Host OS found! Continuing...")
        log.success("OS check test passed")
    else:
        log.warning(
            "OS other than freebsd was found! MirrorManager only fully supports freebsd."
        )
        log.warning(
            "Prerequisites and utility tools will not be installed automatically."
        )
        log.warning(
            "Make sure they are installed before continuing or the tests will fail."
        )
        log.warning(
            "You can cancel this script by hitting Cntrl + C. Continuing in 10s..."
        )
        time.sleep(10)
        log.warn("A test failed but it is not required for MirrorManager to run.")
    pass


# TODO Check if jigdo is installed
async def check_jigdo():
    log.testing('Starting Jigdo Installation Check...')
    pass_or_fail = []
    jigdo_command_list = ["jigdo", "jigdo-lite", "jigdo-full"]
    try:
        with open("configs/jigdo_command.txt", "w") as f:
            if f.readline() in jigdo_command_list:
                log.info("Previous command selection found! passing test...")
                pass
    except:
        for command in jigdo_command_list:
            stream = os.popen(command)
            output = stream.read()
            if "Permission denied" in output:
                log.critical(
                    "A jigdo install was found but the script is unable to access it."
                )
                log.critical(
                    "Either run this script as root (NOT Recommended) or allow it to use the jigdo "
                    "application."
                )
                time.sleep(1)
                raise RequiredTestFailed('Permission Denied to Command')
            elif "command not found" in output:
                log.warning(command + "Not Found on the system... Passing")
                pass_or_fail.append(False)
            else:
                log.info("Command Found! Testing others for compatibility...")
                pass_or_fail.append(command)
                pass
        if pass_or_fail.count(False) < len(jigdo_command_list):
            log.warning(
                "Multiple Jigdo installs were found. Please select which one for MirrorManager to use."
            )
            filtered_list = [x for x in pass_or_fail if x is not False]
            i = 0
            for command in filtered_list:
                print(f"{i}: {command}")
                i = +1
            chosen_command = input('Select via the number. E.g "2"')
            try:
                with open("configs/jigdo_command.txt", "w") as f:
                    f.write(filtered_list[int(chosen_command)])
                    f.close()
                    log.info("Saved Selected option...")
                    pass
            except:
                log.warning("Failed to set the selected command")
                time.sleep(1)
                raise RequiredTestFailed('File Write Failure')
            pass
        elif pass_or_fail.count(False) == len(jigdo_command_list):
            log.critical("Jigdo is not installed on the system.")
            time.sleep(1)
            raise RequiredTestFailed('Jigdo Missing')
    log.success("Jigdo command check test passed")
    pass


# Check mirrors.json is valid
async def validate_json():
    log.testing('Validating Mirror Config...')
    with open("configs/mirrors.json", "r") as f:
        try:
            json.load(f)
            log.success("mirrors.json validation test passed")
            pass
        except ValueError or TypeError as e:
            print("invalid json: %s" % e)
            time.sleep(1)
            raise RequiredTestFailed('JSON Validation Failure')


# TODO Check system/cron scheduling if neither are present give option to select between internal or system

# TODO If one or more fixable tests fail give option to fix then repair



#  Have a custom exception for tests
class RequiredTestFailed(Exception):
    log.fail("A Required Test Failed. This must be fixed before continuing.")
    #sys.exit()


if __name__ == "__main__":
    asyncio.run(disk_space_check())
    asyncio.run(is_connected())
    asyncio.run(compatible_os())
    asyncio.run(check_jigdo())
    asyncio.run(validate_json())