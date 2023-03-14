import os
import sys
import time
import shutil
import socket
import logging


#  Have a custom exception for tests
class RequiredTestFailed(Exception):
    print("A Required Test Failed. This must be fixed before continuing.")
    sys.exit()


class OptionalTestFailed(Exception):
    print("A test failed but it is not required for MirrorManager to run.")
    pass


# Check disk space
async def disk_space_check():
    total, used, free = shutil.disk_usage("/")
    disk_space = [total // (2 ** 30), used // (2 ** 30), free // (2 ** 30)]
    if disk_space[3] < 20:
        raise RequiredTestFailed()
    elif disk_space[3] < 100:
        logging.warning(
            "Although you have enough space for MirrorManager to run, It recommended that you allocate more")
    logging.info("test passed")
    pass


# Check internet connection
async def is_connected():
    pass_or_fail = []
    dns_servers = ['one.one.one.one', '8.8.8.8', '8.8.4.4', '1.0.0.1', '94.140.14.14', '94.140.15.15']
    for dns in dns_servers:
        try:
            logging.info('Pinging' + dns)
            host = socket.gethostbyname(dns)
            s = socket.create_connection((host, 80), 2)
            s.close()
            pass_or_fail.append(True)
            return True
        except Exception:
            logging.critical(f'Ping check for {dns} failed')
            pass
        pass_or_fail.append(False)
        return False
    num_true = pass_or_fail.count(True)
    num_false = pass_or_fail.count(False)
    if num_true < num_false:
        logging.critical('the internet connection test had too many failures')
        raise RequiredTestFailed()
    logging.info("test passed")
    pass


# Check if os is compatible
async def compatible_os():
    if 'freebsd' in sys.platform.startswith('freebsd'):
        logging.info('Freebsd as Host OS found! Continuing...')
    else:
        logging.warning('OS other than freebsd was found! MirrorManager only fully supports freebsd.')
        logging.warning('Prerequisites and utility tools will not be installed automatically.')
        logging.warning('Make sure they are installed before continuing or the tests will fail.')
        logging.warning('You can cancel this script by hitting Cntrl + C. Continuing in 10s...')
        time.sleep(10)
        raise OptionalTestFailed()
    logging.info("test passed")
    pass


# TODO Check if jigdo is installed
async def check_jigdo():
    pass_or_fail = []
    jigdo_command_list = ['jigdo', 'jigdo-lite', 'jigdo-full']
    for command in jigdo_command_list:
        stream = os.popen(command)
        output = stream.read()
        if 'Permission denied' in output:
            logging.critical('A jigdo install was found but the script is unable to access it.')
            logging.critical('Either run this script as root (NOT Recommended) or allow it to use the jigdo '
                             'application.')
            raise RequiredTestFailed()
        elif 'command not found' in output:
            logging.warning(command + 'Not Found on the system... Passing')
            pass_or_fail.append(False)
        else:
            logging.info('Command Found! Testing others for compatibility...')
            pass_or_fail.append(command)
            pass
    if pass_or_fail.count(False) < len(jigdo_command_list):
        logging.warning('Multiple Jigdo installs were found. Please select which one for MirrorManager to use.')
        filtered_list = [x for x in pass_or_fail if x is not False]
        for command in filtered_list:
            print(command)


# TODO Check mirrors.json is valid


# TODO Check system/cron scheduling if neither are present give option to select between internal or system
# TODO If one or more fixable tests fail give option to fix then repair
