import os
import utils
from magic import Magic
from fastapi import APIRouter, status
from fastapi.responses import FileResponse, Response

mime = Magic(mime=True)
logger = utils.Logger()
skm = utils.SqlKeysManagement()
user_api = APIRouter(prefix="/API/v1/GUI")


@user_api.post("/GetDownloadLink")
async def gen_dl_link(file_path: str = None):
    key = await skm.create()
    logger.info(
        f"Generated Download link for File Path: {file_path} with access __token__: {key}"
    )
    sanitized_key = str(key).replace("'", "").replace("{", "").replace("}", "")
    return f"/Pub/GuiDownload?file_path={file_path}&__token__={sanitized_key}"


@user_api.post("/DownloadFile", response_class=FileResponse)
async def download_file(file_path: str = None, __token__: str = None):
    sqlres = await skm.get(__token__)
    if sqlres[0] != 5001:
        if sqlres[0] is not None:  # TODO Fix time checking for tokens < time.time():
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


@user_api.post("/ArchiveSearch")
async def download_file(
    response: Response,
    filename: str = None,
    dir_path: str = f"{os.environ.get('ROOT_PATH')}",
):
    if filename:
        try:
            return await utils.find_files(filename, dir_path)
        except:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {
                "error": 500,
                "msg": "Server failed to search. This could be due to a problem with the api or a malformed client request",
            }
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": 400, "msg": "Search Keyword cannot be empty!"}
