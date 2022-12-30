import os
import time
import uvicorn
import utils
import pymem
from apis import user_api, admin_api, download_file
from magic import Magic
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

app = FastAPI()
logger = utils.Logger()
skm = utils.SqlKeysManagement()
mime = Magic(mime=True)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# START USER PATHS
# GET PATHS
@app.get("/")
async def root():
    return RedirectResponse("/Home")


@app.get("/Home")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/ListDirectory", response_class=HTMLResponse)
async def list_dir(request: Request, dir_path: str = r"/public"):
    if '/GitStorage' in dir_path:
        return RedirectResponse("/Git")
    if os.path.exists(f'{os.environ.get("ROOT_PATH")}{dir_path}'):
        if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{dir_path}'):
            return RedirectResponse(f"/FileInfo?file_path={dir_path}")
        dir_info = os.scandir(f'{os.environ.get("ROOT_PATH")}{dir_path}')
        logger.info(f'Requested List Directory of "{dir_path}"')
        return templates.TemplateResponse(
            "listdir.html",
            {"request": request, "dir_info": dir_info, "dir_path": dir_path},
        )
    logger.warning(f'Requested File Directory ("{dir_path}") that does not exist')
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": "File Directory does not exist"}
    )


@app.get("/FileInfo", response_class=HTMLResponse)
async def file_info(request: Request, file_path: str = None):
    if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{file_path}'):
        filename = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path).replace("\\", "/")
        data = os.stat(f'{os.environ.get("ROOT_PATH")}{file_path}')
        creation_date = datetime.fromtimestamp(data.st_ctime, tz=timezone.utc)
        modified_date = datetime.fromtimestamp(data.st_mtime, tz=timezone.utc)
        media_type = mime.from_file(f'{os.environ.get("ROOT_PATH")}{file_path}')
        logger.info(f'Requested File information for "{file_path}"')
        return templates.TemplateResponse(
            "fileinfo.html",
            {
                "request": request,
                "file_path": file_path,
                "filename": filename,
                "dir_path": dir_path,
                "creation_date": creation_date,
                "modified_date": modified_date,
                "file_size": utils.convert_size(data.st_size),
                "media_type": media_type,
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
        },
    )


@app.get("/GuiDownload", response_class=HTMLResponse)
async def gui_download(request: Request, file_path: str = None, __token__: str = None):
    if await skm.get(__token__):
        if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{file_path}'):
            data = os.stat(f'{os.environ.get("ROOT_PATH")}{file_path}')
            filename = os.path.basename(file_path)
            return templates.TemplateResponse(
                "guidownload.html",
                {
                    "request": request,
                    "filename": filename,
                    "file_size": utils.convert_size(data.st_size),
                    "__token__": __token__,
                    "file_path": file_path,
                },
            )
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "File No Longer Exists. It may "
                "of been removed or have moved "
                "locations.",
            },
        )
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": "Invalid Download Token"}
    )


@app.get("/DirectDownload")
async def direct_download(file_path: str = None, __token__: str = None):
    logger.info(f"Direct Download of File Requested. File Info Below")
    return download_file(file_path, __token__)


# END USER PATHS
# START ADMINISTRATOR PATHS

aum = utils.AdministratorUserManagement()
admin_router = APIRouter(prefix="/AdministratorArea")
manager = LoginManager(os.environ.get("SECRET"), token_url="/OAuth/Token")


class NotAuthenticatedException(Exception):
    pass


def exc_handler(request, exc):
    return RedirectResponse(url="/OAuth/Login")


manager.not_authenticated_exception = NotAuthenticatedException
app.add_exception_handler(NotAuthenticatedException, exc_handler)


@manager.user_loader()
def load_user(email: str):
    user = aum.grab_usr(email)
    return user


# GET PATHS
@admin_router.get("/")
async def admin_root():
    return RedirectResponse("Panel")


@admin_router.get("/OAuth/Login")
async def admin_root(request: Request):
    return templates.TemplateResponse("administrator/panel.html", {"request": request})


@app.post("/OAuth/Token")
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password
    user = load_user(email)
    if not user:
        raise InvalidCredentialsException
    elif password != user["password"]:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=email), expires=timedelta(hours=12)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@admin_router.get("/OAuth/Logout")
async def admin_root(request: Request):
    return templates.TemplateResponse("administrator/panel.html", {"request": request})


@admin_router.get("/Panel", response_class=HTMLResponse)
async def admin_root(request: Request, __action__: str = None):
    if __action__ == "GitRepositories":
        return templates.TemplateResponse(
            "administrator/git.html", {"request": request}
        )
    elif __action__ == "FileMirrors":
        return templates.TemplateResponse(
            "administrator/files.html", {"request": request}
        )
    elif __action__ == "UpdateMonitors":
        return templates.TemplateResponse(
            "administrator/monitors.html", {"request": request}
        )
    return templates.TemplateResponse("administrator/panel.html", {"request": request})


# END ADMINISTRATOR PATHS
# MIDDLEWARE PATHS
@app.middleware("http")
async def time_response(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 3))
    return response


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = "static/favicon.ico"
    return FileResponse(favicon_path)


app.include_router(user_api)
app.include_router(admin_api)
app.include_router(admin_router)

if __name__ == "__main__":
    pymem.optimise_mem()
    utils.loaded()
    print("LOG:      (main.py) - Starting MirrorManager process")
    uvicorn.run(app, host="127.0.0.1", port=8000)
