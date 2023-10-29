import os
import time
import uvicorn
import utils.utils as utils
import initialize
import random
from apis import user_api, download_file
from magic import Magic
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime, timezone
from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functools import wraps

app = FastAPI()
logger = utils.Logger()
skm = utils.SqlKeysManagement()
mime = Magic(mime=True)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
app.mount("/Static", StaticFiles(directory="Static"), name="Static")
templates = Jinja2Templates(directory="templates")


def time_it(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        start_time = time.time()
        response = await func(request, *args, **kwargs)
        end_time = time.time()
        load_time = end_time - start_time
        setattr(request.state, 'page_load_time', load_time)
        return response

    return wrapper


def temp_template_time():
    return random.randint(5, 100)


@app.get("/")
async def root():
    return RedirectResponse("/Home")


@app.get("/Home")
@time_it
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "template_time": temp_template_time()})


pub_files = APIRouter(prefix="/Pub")


@pub_files.get("/ListDirectory", response_class=HTMLResponse)
async def list_dir(request: Request, dir_path: str = r"/"):
    if "/GitStorage" in dir_path:
        return RedirectResponse("https://code.t2v.city/Gitea")
    if os.path.exists(f'{os.environ.get("ROOT_PATH")}{dir_path}'):
        if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{dir_path}'):
            return RedirectResponse(f"/Pub/FileInfo?file_path={dir_path}")
        dir_info = os.scandir(f'{os.environ.get("ROOT_PATH")}{dir_path}')
        logger.info(f'Requested List Directory of "{dir_path}"')
        dir_list_filtered = [
            entry.name for entry in dir_info if not "MM_DONT_INCLUDE-" in entry.name
        ]
        dir_list = list(dir_list_filtered)
        return templates.TemplateResponse(
            "listdir.html",
            {
                "request": request,
                "dir_list": dir_list,
                "dir_path": dir_path,
                "template_time": temp_template_time(),
            },
        )
    logger.warning(f'Requested File Directory ("{dir_path}") that does not exist')
    return templates.TemplateResponse(
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
        return templates.TemplateResponse(
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
    return templates.TemplateResponse(
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
            return templates.TemplateResponse(
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
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "File No Longer Exists. It may "
                         "of been removed or have moved "
                         "locations.",
                "template_time": temp_template_time()
            },
        )
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": "Invalid Download Token", "template_time": temp_template_time()}
    )


@pub_files.get("/SearchFiles")
async def search_files(request: Request, __in__: str = f"Root", dir_path: str = "Root"):
    return templates.TemplateResponse(
        "search.html", {"request": request, "search_action": dir_path, "template_time": temp_template_time()}
    )


@pub_files.get("/DirectDownload")
async def direct_download(file_path: str = None, __token__: str = None):
    logger.info(f"Direct Download of File Requested. File Info:")
    return download_file(file_path, __token__)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = "Static/favicon.ico"
    return FileResponse(favicon_path)


# @app.get("/sentry-debug")
# async def trigger_error():
#    division_by_zero = 1 / 0


app.include_router(user_api)
app.include_router(pub_files)

if __name__ == "__main__":
    initialize.optimise_mem()
    # initialize.start_sentry_sdk()
    utils.loaded()
    print("LOG:      (main.py) - Starting MirrorManager process")
    uvicorn.run(app, host="127.0.0.1", port=8000)
