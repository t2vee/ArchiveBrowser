import os
import urllib.request
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
import json


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

async def download_url(url, dest_path):
    parsed_url = urlparse(url)
    subpath = parsed_url.path.split('/')
    print(len(subpath))
    if subpath[-1] == '':
        subpath = subpath[:-1]
    if subpath[0] == '':
        subpath = subpath[1:]
    if len(subpath) > 1:
        subpath = subpath[1:]
    else:
        subpath = []
    os.makedirs(dest_path, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        if response.info().get_content_type() == 'text/html':
            html = response.read().decode('utf-8')
            for link in get_links(html, url):
                link_subpath = link.split('/')
                if link_subpath[-1] == '':
                    link_subpath = link_subpath[:-1]
                if link_subpath[0] == '':
                    link_subpath = link_subpath[1:]
                if len(link_subpath) > len(subpath):
                    print("============DIR_PATH_DEBUGGING==============")
                    print(subpath)
                    print(len(subpath))
                    print("--------------")
                    print(link_subpath)
                    print(len(link_subpath))
                    print("--------------")
                    link_subpath = link_subpath[len(subpath):]

                    sub_dest_path = os.path.join(dest_path, *link_subpath)
                    print(sub_dest_path)
                    print("============DIR_PATH_DEBUGGING_END==============")
                    await download_url(link, sub_dest_path)
        # Handle files
        else:
            filename = os.path.basename(parsed_url.path)
            filepath = os.path.join(dest_path, filename)
            with open(filepath, 'wb') as f:
                f.write(response.read())

def get_links(html, base_url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a')]
    base_parsed = urlparse(base_url)
    links = [urljoin(base_url, link) for link in links]
    return links

async def load_file_mirror_config():
    with open('configs/mirrors.json', 'r') as f:
        config = json.load(f)
        for mirror, info in config.items():
            url = info['info']['url']
            dir_suffix = info['info']['dir_suffix']
            unix_dir_path = os.environ.get('ROOT_PATH').replace("\\", "/")
            dest_path = f"{unix_dir_path}{dir_suffix}"
            await download_url(url, dest_path)
    f.close()
    return "temp"

async def main():
    await load_file_mirror_config()

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()