import os
import re
import requests
from urllib.parse import urlparse
import utils.utils as utils
from magic import Magic
from fastapi import APIRouter, status, Form, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from Database import get_db, ModBasedUponModrinthMetaData
from typing import List, Dict

def _get_modrinth_mod_id_from_url(mod_link: str):
    """
    Extracts the mod ID/slug from the Modrinth mod URL.
    """
    match = re.search(r'https:\/\/modrinth\.com\/mod\/([\w-]+)', mod_link)
    if match:
        return match.group(1)
    else:
        return None


def _validate_and_get_modrinth_mod_metadata(mod_link: str):
    """
    Validates the Modrinth mod link and retrieves mod metadata from Modrinth API.
    Returns the mod metadata if the mod exists, otherwise raises an HTTPException.
    """
    mod_id = _get_modrinth_mod_id_from_url(mod_link)
    if not mod_id:
        raise HTTPException(status_code=400, detail="Invalid Modrinth mod link.")

    api_url = f"https://api.modrinth.com/v2/project/{mod_id}"
    response = requests.get(api_url)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Modrinth mod not found.")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to retrieve mod metadata.")

    mod_metadata = response.json()
    return mod_metadata


def _get_curseforge_mod_id_from_url(mod_link: str):
    """
    Extracts the mod ID from the CurseForge mod URL.
    This is a placeholder function and needs to be adapted based on how the mod ID can be resolved.
    """
    # Placeholder implementation
    # Replace with actual logic to extract or resolve the mod ID from the URL
    return None

def _validate_and_get_curseforge_mod_metadata(mod_link: str):
    """
    Validates the CurseForge mod link and retrieves mod metadata from the CurseForge API.
    Returns the mod metadata if the mod exists, otherwise raises an HTTPException.
    """
    mod_id = _get_curseforge_mod_id_from_url(mod_link)
    if not mod_id:
        raise HTTPException(status_code=400, detail="Invalid or unsupported CurseForge mod link.")

    api_url = f"https://api.curseforge.com/v1/mods/{mod_id}"
    headers = {
        'Accept': 'application/json',
        'x-api-key': os.environ.get('CURSEFORGE_API_KEY')
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="CurseForge mod not found.")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to retrieve mod metadata.")

    mod_metadata = response.json().get("data", {})
    return mod_metadata


def get_mod_metadata(mod_link: str):
    """
    Validates the mod link and retrieves metadata from the appropriate API.
    Calls the respective function based on whether the link is from Modrinth or CurseForge.
    """
    parsed_url = urlparse(mod_link)
    domain = parsed_url.netloc

    try:
        if 'modrinth.com' in domain:
            return _validate_and_get_modrinth_mod_metadata(mod_link)
        elif 'curseforge.com' in domain:
            return _validate_and_get_curseforge_mod_metadata(mod_link)
        else:
            raise HTTPException(status_code=400, detail="Unsupported mod provider.")
    except HTTPException as e:
        # Propagate the exception for handling in the endpoint
        raise e


def mod_exists(mod_id: str, db: Session) -> bool:
    """
    Checks if a mod with the given ID already exists in the database.
    """
    return db.query(ModBasedUponModrinthMetaData).filter(ModBasedUponModrinthMetaData.id == mod_id).first() is not None


async def get_mod_details_from_slugs(slugs: str, db: Session) -> List[Dict[str, str]]:
    """
    Takes a comma-separated string of mod slugs, queries the database for corresponding mod IDs and names,
    and returns a list of dictionaries with these details.

    :param slugs: Comma-separated string of mod slugs.
    :param db: SQLAlchemy database session.
    :return: List of dictionaries containing mod IDs and names.
    """
    slug_list = slugs.split(',')
    mod_details = db.query(ModBasedUponModrinthMetaData.id, ModBasedUponModrinthMetaData.title).filter(ModBasedUponModrinthMetaData.slug.in_(slug_list)).all()
    return [{"id": mod_id, "name": mod_title} for mod_id, mod_title in mod_details]


