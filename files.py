import os
import sql
from dotenv import load_dotenv

load_dotenv()


async def get_dir(dir_path: str = f"{os.environ.get('ROOT_PATH')}/public/"):
    dir_entries = os.scandir(dir_path)
    return dir_entries


async def grab_file_path(file_uuid: str = None):

    return file_path


async def grab_file_meta(file_uuid: str = None):
    f = os.stat(os.environ.get('ROOT_PATH') + grab_file_path(file_uuid))

    return "nuts"


async def check_uuid():
    return 'deez'
