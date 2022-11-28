import tokens
import logger
import gc
import files
import uvicorn
import grab_latest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# gc.collect(2)
# gc.freeze()

# allocs, gen1, gen2 = gc.get_threshold()
# allocs = 50_000
# gen1 = gen1 * 2
# gen2 = gen2 * 2
# gc.set_threshold(allocs, gen1, gen2)

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
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


@app.get("/GuiDownload", response_class=HTMLResponse)
async def guid_download(request: Request, file_uuid: str = None, __token__: str = None):
    if tokens.get(__token__):
        if files.check_uuid(file_uuid):
            data = await files.grab_file_meta(file_uuid)
            return templates.TemplateResponse("guidownload.html", {"request": request, "file_data": data})
        return templates.TemplateResponse("error.html", {"request": request, 'error': 'File No Longer Exists. It may '
                                                                                      'of been removed or have moved '
                                                                                      'locations.'})
    return templates.TemplateResponse("error.html", {"request": request, "error": 'Invalid Download Token'})


@app.get("/DirectDownload")
async def direct_download(request: Request, __token__: str = None):
    return "temp"


# POST PATHS
@app.post("/API/v1/GetDownloadLink")
async def gen_dl_link(file_uuid: str = None):
    key = await tokens.create()
    return f'/GuiDownload?file_uuid={file_uuid}&__token__={key}'


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
