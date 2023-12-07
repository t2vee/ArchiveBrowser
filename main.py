import os
import time
import uvicorn
import utils.utils as utils
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
from sqlalchemy.orm import Session

from Database import SessionLocal, engine, Base

app = FastAPI()
logger = utils.Logger()
skm = utils.SqlKeysManagement()
mime = Magic(mime=True)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
app.mount("/Static", StaticFiles(directory="static"), name="Static")


@app.get("/")
async def root():
    return 'haii'


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = "Static/favicon.ico"
    return FileResponse(favicon_path)


from FileBrowserAPI import file_browser_api
from FileBrowser import pub_files

app.include_router(pub_files)
app.include_router(file_browser_api)

from ModArchives import mc_mods
from ModArchivesAPI import mc_mods_api

app.include_router(mc_mods)
app.include_router(mc_mods_api)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("LOG:      (Database.py) - Successfully created database connection")
    initialize.optimise_mem()
    # initialize.start_sentry_sdk()
    utils.loaded()
    print("LOG:      (main.py) - Starting MirrorManager process")
    uvicorn.run(app, host="127.0.0.1", port=8000)
