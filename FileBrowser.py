import os
import time
import uvicorn
import utils.utils as utils
from utils.utils import cache, cache_key, time_it, temp_template_time
import initialize
import random
from cachetools import cached, LRUCache
from magic import Magic
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime, timezone
from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functools import wraps

from FileBrowserAPI import download_file

logger = utils.Logger()
skm = utils.SqlKeysManagement()
mime = Magic(mime=True)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

file_browser_templates = Jinja2Templates(directory="templates/FileBrowser")
pub_files = APIRouter(prefix="/FileBrowser")


@pub_files.get("/Home")
@time_it
async def home(request: Request):
    return file_browser_templates.TemplateResponse("home.html", {"request": request, "template_time": temp_template_time()})


@cached(cache, key=cache_key)
@pub_files.get("/ListDirectory", response_class=HTMLResponse)
async def list_dir(request: Request, dir_path: str = r"/"):
    if os.path.exists(f'{os.environ.get("ROOT_PATH")}{dir_path}'):
        if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{dir_path}'):
            return RedirectResponse(f"/FileBrowser/FileInfo?file_path={dir_path}")
        dir_info = os.scandir(f'{os.environ.get("ROOT_PATH")}{dir_path}')
        dir_list = []
        for entry in dir_info:
            if "MM_DONT_INCLUDE-" not in entry.name:
                data = entry.stat()
                dir_list.append({
                    "name": entry.name,
                    "size": utils.convert_size(data.st_size),
                    "modified_date": datetime.fromtimestamp(data.st_mtime, tz=timezone.utc).strftime('%Y-%b-%d %H:%M')
                })
        path_segments = [{"name": "Root", "url": "/FileBrowser/ListDirectory"}]
        full_path = ""
        for segment in dir_path.strip("/").split("/"):
            full_path += segment + "/"
            path_segments.append({"name": segment, "url": f"/FileBrowser/ListDirectory?dir_path=/{full_path}"})
        return file_browser_templates.TemplateResponse(
            "listdir.html",
            {
                "request": request,
                "dir_list": dir_list,
                "dir_path": dir_path,
                "template_time": temp_template_time(),
                "path_segments": path_segments},
        )
    logger.warning(f'Requested File Directory ("{dir_path}") that does not exist')
    return file_browser_templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "File Directory does not exist", "template_time": temp_template_time()}
    )


@pub_files.get("/FileInfo", response_class=HTMLResponse)
async def file_info(request: Request, file_path: str = None):
    if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{file_path}'):
        filename = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path).replace("\\", "/")
        data = os.stat(f'{os.environ.get("ROOT_PATH")}{file_path}')
        file_sha256 = await utils.grab_sha256(dir_path, filename)
        logger.info(f'Requested File information for "{file_path}"')
        return file_browser_templates.TemplateResponse(
            "fileinfo.html",
            {
                "request": request,
                "file_path": file_path,
                "filename": filename,
                "dir_path": dir_path,
                "creation_date": datetime.fromtimestamp(data.st_ctime, tz=timezone.utc),
                "modified_date": datetime.fromtimestamp(data.st_mtime, tz=timezone.utc),
                "file_size": utils.convert_size(data.st_size),
                "media_type": mime.from_file(
                    f'{os.environ.get("ROOT_PATH")}{file_path}'
                ),
                "template_time": temp_template_time(),
                "file_sha": file_sha256,
            },
        )
    logger.warning(f'Requested File information for Non-Existent file: "{file_path}"')
    return file_browser_templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": "File No Longer Exists. It may "
                     "of been removed or have moved "
                     "locations.",
            "template_time": temp_template_time()
        },
    )


@pub_files.get("/GuiDownload", response_class=HTMLResponse)
async def gui_download(request: Request, file_path: str = None, __token__: str = None):
    if await skm.get(__token__):
        if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{file_path}'):
            data = os.stat(f'{os.environ.get("ROOT_PATH")}{file_path}')
            filename = os.path.basename(file_path)
            file_sha256 = utils.check_sha256(file_path, filename)
            return file_browser_templates.TemplateResponse(
                "guidownload.html",
                {
                    "request": request,
                    "filename": filename,
                    "file_size": utils.convert_size(data.st_size),
                    "__token__": __token__,
                    "file_path": file_path,
                    "file_sha": file_sha256,
                    "template_time": temp_template_time()
                },
            )
        return file_browser_templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "File No Longer Exists. It may "
                         "of been removed or have moved "
                         "locations.",
                "template_time": temp_template_time()
            },
        )
    return file_browser_templates.TemplateResponse(
        "error.html", {"request": request, "error": "Invalid Download Token", "template_time": temp_template_time()}
    )


@pub_files.get("/SearchFiles")
async def search_files(request: Request, __in__: str = f"Root", dir_path: str = "Root"):
    return file_browser_templates.TemplateResponse(
        "search.html", {"request": request, "search_action": dir_path, "template_time": temp_template_time()}
    )


@pub_files.get("/DirectDownload")
async def direct_download(file_path: str = None, __token__: str = None):
    logger.info(f"Direct Download of File Requested. File Info:")
    return download_file(file_path, __token__)