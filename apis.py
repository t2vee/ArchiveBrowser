import os
import utils
from magic import Magic
from fastapi import APIRouter
from fastapi.responses import FileResponse

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