import tokens
import logger
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# GET PATHS
@app.get("/")
async def root():
    return RedirectResponse("/ListDirectory")


@app.get("/ListDirectory", response_class=HTMLResponse)
async def list_dir(request: Request, dir_path: str = r'/public'):
    return templates.TemplateResponse("listdir.html", {"request": request})


@app.get("/FileInfo", response_class=HTMLResponse)
async def file_info(request: Request, file_uuid: str = None):
    return templates.TemplateResponse("fileinfo.html", {"request": request})


@app.get("/DirectDownload/", response_class=HTMLResponse)
async def direct_download(request: Request, __token__: str = None):

    return templates.TemplateResponse("directdownload.html", {"request": request})


# POST PATHS
@app.post("/API/v1/GetDownloadLink")
async def gen_dl_link():
    key = await tokens.create()

    return "temp"