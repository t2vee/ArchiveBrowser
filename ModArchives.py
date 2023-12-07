import os
import time
import uvicorn
import utils.utils as utils
from utils.utils import cache, cache_key, time_it, temp_template_time
import initialize
import markdown
import random
from cachetools import cached, LRUCache
from magic import Magic
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime, timezone
from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functools import wraps

from Database import get_db, ModBasedUponModrinthMetaData
from sqlalchemy.orm import Session
from ModArchivesTools import get_mod_details_from_slugs

logger = utils.Logger()
skm = utils.SqlKeysManagement()
mime = Magic(mime=True)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

mc_mods_templates = Jinja2Templates(directory="templates/McModsArchive")
mc_mods = APIRouter(prefix="/MCModsArchive")


@mc_mods.get("/Home")
async def home(request: Request):
    return mc_mods_templates.TemplateResponse("Home.html", {"request": request})


@mc_mods.get("/Browse")
async def browse_mods(request: Request):
    return mc_mods_templates.TemplateResponse("Browse.html", {"request": request})


@mc_mods.get("/ModInformation")
async def browse_mods(request: Request, id: str = None, db: Session = Depends(get_db)):
    if id is None:
        raise HTTPException(status_code=404, detail="Mod ID not provided")
    mod = db.query(ModBasedUponModrinthMetaData).filter(ModBasedUponModrinthMetaData.id == id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Mod not found")
    mod_desc = markdown.markdown(mod.body)
    return mc_mods_templates.TemplateResponse("ModInfo.html", {"request": request, "mod": mod, "mod_desc": mod_desc})


@mc_mods.get("/UploadNewContent")
async def upload_content(request: Request):
    return mc_mods_templates.TemplateResponse("Upload.html", {"request": request})


@mc_mods.get("/UploadSuccess")
async def upload_content_success(request: Request, slugs: str = '', db: Session = Depends(get_db)):
    if not slugs:
        return RedirectResponse("/MCModsArchive/UploadNewContent")
    mods = await get_mod_details_from_slugs(slugs, db)
    return mc_mods_templates.TemplateResponse("UploadSuccess.html", {"request": request, "mods": mods})