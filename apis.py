import os
import git
import utils
import json
import shutil
from magic import Magic
from urllib.parse import urlparse
from datetime import datetime
from fastapi import APIRouter, Form
from fastapi.responses import FileResponse, RedirectResponse

mime = Magic(mime=True)
logger = utils.Logger()
skm = utils.SqlKeysManagement()
aum = utils.AdministratorUserManagement()
apd = utils.AdministratorPanelDB()
user_api = APIRouter(prefix="/API/v1/GUI")


@user_api.post("/GetDownloadLink")
async def gen_dl_link(file_path: str = None):
    key = await skm.create()
    logger.info(
        f"Generated Download link for File Path: {file_path} with access __token__: {key}"
    )
    sanitized_key = str(key).replace("'", "").replace("{", "").replace("}", "")
    return f"/GuiDownload?file_path={file_path}&__token__={sanitized_key}"


@user_api.post("/DownloadFile", response_class=FileResponse)
async def download_file(file_path: str = None, __token__: str = None):
    sqlres = await skm.get(__token__)
    if sqlres[0] != 5001:
        if sqlres[0] is not None:  # < time.time(): TODO Fix time checking for tokens
            if os.path.isfile(f'{os.environ.get("ROOT_PATH")}{file_path}'):
                await skm.delete(__token__)
                filename = f"t2vArchive-MirrorManager_{os.path.basename(file_path)}"
                media_type = mime.from_file(f'{os.environ.get("ROOT_PATH")}{file_path}')
                headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
                logger.info(
                    f"File Download Started. File UUID: {file_path}, File Name: {filename}, File Type: {media_type}"
                )
                return FileResponse(
                    path=f"{os.environ.get('ROOT_PATH')}{file_path}",
                    headers=headers,
                    filename=filename,
                    media_type=media_type,
                )
            m = {
                "code": 404,
                "error": "File no longer exists. It may of been deleted or moved",
            }
            logger.warning(m)
            return m
        m = {"code": 401, "error": "Download Token has Expired"}
        logger.warning(m)
        return m
    m = {"code": 401, "error": "Invalid Download Token!"}
    logger.warning(m)
    return m


# ADMIN API ROUTER
admin_api = APIRouter(prefix="/API/v1/ADMIN")


@admin_api.post("/CloneNewGitRepo")
async def clone_new_repo(
        git_endpoint: str = Form(),
        monitor_repo: str = Form(0),
        monitor_interval: int = Form(0),
):
    git_url = urlparse(git_endpoint)
    try:
        git.Repo.clone_from(git_endpoint, f"{os.environ.get('ROOT_PATH')}/GitStorage/{git_url.path.lstrip('/')}")
    except:
        logger.critical(f"Cloning of Git Repo {git_endpoint} Failed.")
        return {"error": "Git Endpoint URL is invalid or this repository already exists", "code": 500}
    clone_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    git_array = [
        git_endpoint,
        git_url.path.lstrip("/"),
        monitor_repo,
        monitor_interval,
        clone_date,
    ]
    try:
        await apd.create_new_git_instance(git_array)
    except:
        await delete_repo(git_endpoint)
        return {
            "error": "Failed to add repo to internal database due to a internal server error",
            "code": 500,
        }
    return "success"  # TODO fix response handling to post request


@admin_api.post("/DeleteGitRepo")
async def delete_repo(git_endpoint: str = None):
    git_url = urlparse(git_endpoint)
    try:
        shutil.rmtree(f"{os.environ.get('ROOT_PATH')}{git_url.path.lstrip('/')}")
    except:
        return {
            "error": "Failed to delete Repo directory due to a internal server error",
            "code": 500,
        }
    try:
        await apd.delete_git_repo(git_endpoint)
    except:
        return {
            "error": "Failed to delete Repo from internal database due to a internal server error",
            "code": 500,
        }
    return "success"


@admin_api.post("/ListGitRepos")
async def list_git_repos():
    response = await apd.get_git_repos()
    json_res = json.loads(response)
    if json_res[0] == 5001:
        return {
            "message": "There are currently no git repositories set up",
            "code": 5001,
        }
    return json_res


@admin_api.post("/ModifyGitMonitorSettings")
async def clone_new_repo(git_endpoint: str = None):
    response = await apd.get_git_repo_info(git_endpoint)
    json_res = json.loads(response)
    return json_res
