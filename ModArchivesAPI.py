import os
import re
import time
import requests
from urllib.parse import urlparse
import utils.utils as utils
from magic import Magic
from fastapi import APIRouter, status, Form, HTTPException, Depends
from fastapi.responses import FileResponse, Response, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from Database import get_db, ModBasedUponModrinthMetaData
from ModArchivesTools import get_mod_metadata, mod_exists

mime = Magic(mime=True)
logger = utils.Logger()
skm = utils.SqlKeysManagement()
mc_mods_api = APIRouter(prefix="/API/v1/MCModsArchive/GUI")


@mc_mods_api.post("/SubmitContentLink")
async def submit_content_link(mod_links: str = Form(...), db: Session = Depends(get_db)):
    links = mod_links.split('\n')
    results = []
    has_error = False

    for link in links:
        if link.strip():
            try:
                mod_metadata = get_mod_metadata(link.strip())

                if mod_exists(mod_metadata['id'], db):
                    results.append({"link": link, "status": "error", "message": "Mod already exists in the database."})
                    has_error = True
                    continue

                mod_instance = ModBasedUponModrinthMetaData.from_json(mod_metadata)
                db.add(mod_instance)
                results.append({"slug": link.replace('https://modrinth.com/mod/', ''), "status": "success"})
            except HTTPException as e:
                results.append({"link": link, "status": "error", "message": str(e.detail)})
                has_error = True
            except Exception as e:
                results.append({"link": link, "status": "error", "message": str(e)})
                has_error = True

    if has_error:
        db.rollback()
        return JSONResponse(status_code=400, content=results)
    else:
        try:
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            return JSONResponse(status_code=500, content={"status": "error",
                                                          "message": "Database error occurred while saving the mods."})

    return JSONResponse(status_code=200, content=results)
