import os
import utils.utils as utils
from magic import Magic
from fastapi import APIRouter, status, Form
from fastapi.responses import FileResponse, Response

mime = Magic(mime=True)
logger = utils.Logger()
skm = utils.SqlKeysManagement()
file_browser_api = APIRouter(prefix="/API/v1/FileBrowser/GUI")


@file_browser_api.post("/GetDownloadLink")
async def gen_dl_link(file_path: str = None):
    key = await skm.create()
    logger.info(
        f"Generated Download link for File Path: {file_path} with access __token__: {key}"
    )
    sanitized_key = str(key).replace("'", "").replace("{", "").replace("}", "")
    return f"/Pub/GuiDownload?file_path={file_path}&__token__={sanitized_key}"


async def er(code, error_message):
    logger.warning({"code": code, "error": error_message})
    return {"code": code, "error": error_message}


@file_browser_api.post("/DownloadFile", response_class=FileResponse)
async def download_file(file_path: str = None, __token__: str = None):
    sqlres = await skm.get(__token__)

    if sqlres[0] == 5001:
        return await er(401, "Invalid Download Token!")

    if sqlres[0] is None:  # TODO: Consider adding token expiration time check here
        return await er(401, "Download Token has Expired")

    abs_file_path = f'{os.environ.get("ROOT_PATH")}{file_path}'

    if not os.path.isfile(abs_file_path):
        return await er(404, "File no longer exists. It may have been deleted or moved")

    await skm.delete(__token__)

    filename = f"t2vArchive-MirrorManager_{os.path.basename(file_path)}"
    media_type = mime.from_file(abs_file_path)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    logger.info(
        f"File Download Started. File UUID: {file_path}, File Name: {filename}, File Type: {media_type}"
    )

    return FileResponse(
        path=abs_file_path,
        headers=headers,
        filename=filename,
        media_type=media_type,
    )


@file_browser_api.post("/ArchiveSearch")
async def download_file(
        response: Response,
        search_request: str = Form(...),
        dir_path: str = Form(None),
):
    if search_request:
        root_path = os.environ.get("ROOT_PATH")
        if dir_path is None:
            dir_path = root_path
            search_results = utils.find_files(search_request, dir_path)
        else:
            search_results = utils.find_files(search_request, dir_path)
        search_results = [result.replace(root_path, "").replace("\\", "/") for result in search_results]
        if search_results:
            return search_results
        return {0: "No Results Found"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": 400, "msg": "Search Keyword cannot be empty!"}
