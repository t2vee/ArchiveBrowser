import os
import urllib.request
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from time import sleep
import json

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


async def load_file_mirror_config():
    with open("configs/mirrors.json", "r") as f:
        config = json.load(f)
        for mirror, info in config.items():
            unix_dir_path = os.environ.get("ROOT_PATH").replace("\\", "/")
            dest_path = f'{unix_dir_path}{info["info"]["dir_suffix"]}'
            try:
                os.system("cls" if os.name == "nt" else "clear")
                print(
                    "========================= ! IMPORTANT ! ========================="
                )
                print("Downloading all files from " + info["info"]["url"])
                print(
                    "Depending on the size of the Filesystem, this may take a while..."
                )
                print("To cancel the operation, repeatedly press Cntrl + C")
                print(
                    "This message will disappear in 10 seconds and you will receive the download output"
                )
                print(
                    "========================= ! IMPORTANT ! ========================="
                )
                sleep(10)
                os.system("cls" if os.name == "nt" else "clear")
                os.system(f'wget -r -np -nH {info["info"]["url"]} -P {dest_path}')
            except:
                print("Download failed for " + info["info"]["url"])
    f.close()
    return "File Sync Complete"


if __name__ == "__main__":
    asyncio.run(load_file_mirror_config())
