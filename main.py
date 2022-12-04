import sql
import logger
import gc
import os
import files
import uvicorn
from dotenv import load_dotenv
import grab_latest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

gc.collect(2)
gc.freeze()

allocs, gen1, gen2 = gc.get_threshold()
allocs = 50_000
gen1 = gen1 * 2
gen2 = gen2 * 2
gc.set_threshold(allocs, gen1, gen2)

app = FastAPI()
load_dotenv()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# GET PATHS
@app.get("/")
async def root():
    return RedirectResponse("/ListDirectory")


@app.get("/ListDirectory", response_class=HTMLResponse)
async def list_dir(request: Request, dir_path: str = r'/public'):
    dir_info = files.get_dir(dir_path)
    return templates.TemplateResponse("listdir.html", {"request": request, "dir_info": dir_info})


@app.get("/FileInfo", response_class=HTMLResponse)
async def file_info(request: Request, file_uuid: str = None):
    if files.check_uuid(file_uuid):
        data = await files.grab_file_meta(file_uuid)
        return templates.TemplateResponse("fileinfo.html", {"request": request, "file_data": data})
    return templates.TemplateResponse("error.html", {"request": request, 'error': 'File No Longer Exists. It may '
                                                                                  'of been removed or have moved '
                                                                                  'locations.'})


@app.get("/GuiDownload", response_class=HTMLResponse)
async def gui_download(request: Request, file_uuid: str = None, __token__: str = None):
    if sql.get(__token__):
        if files.check_uuid(file_uuid):
            data = await files.grab_file_meta(file_uuid)
            return templates.TemplateResponse("guidownload.html", {"request": request, "file_data": data})
        return templates.TemplateResponse("error.html", {"request": request, 'error': 'File No Longer Exists. It may '
                                                                                      'of been removed or have moved '
                                                                                      'locations.'})
    return templates.TemplateResponse("error.html", {"request": request, "error": 'Invalid Download Token'})


@app.get("/DirectDownload")
async def direct_download(file_uuid: str = None, __token__: str = None):
    logger.info(f'Direct Download of File Requested. File Info Below')
    return download_file(file_uuid, __token__)


# POST PATHS
@app.post("/API/v1/GUI/GetDownloadLink")
async def gen_dl_link(file_uuid: str = None):
    key = await sql.create()
    logger.info(f'Generated Download link for File UUID: {file_uuid} with access __token__: {key}')
    return f'/GuiDownload?file_uuid={file_uuid}&__token__={key}'


@app.post("/API/v1/GUI/DownloadFile")
async def download_file(file_uuid: str = None, __token__: str = None):
    if sql.get(__token__):
        if files.check_uuid(file_uuid):
            data = await files.grab_file_meta(file_uuid)
            logger.info(f'File Download Started. File UUID: {file_uuid}, File Name: {data[0]}, File Type: {data[2]}')
            await sql.delete(__token__)
            return FileResponse(path=os.environ.get('ROOT_PATH'), filename=data[0], media_type=data[2])
        m = {'code': 404, 'error': 'File no longer exists. It may of been deleted or moved'}
        logger.warning(m)
        return m
    m = {'code': 401, 'error': 'Invalid Download Token!'}
    logger.warning(m)
    return m


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
