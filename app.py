from typing import List, Dict
from fastapi import FastAPI, responses, status
from pydantic import BaseModel
from submodules.model.business_objects import general
import util
import config_handler

app = FastAPI()


@app.post("/update_to_newest")
def update_to_newest() -> str:
    session_token = general.get_ctx_token()
    if util.update_to_newest():
        msg = "updated to current version"
    else:
        msg = "nothing to update"
    general.remove_and_refresh_session(session_token)
    return msg, 200


@app.get("/version_overview")
def version_overview() -> List[Dict[str, str]]:
    session_token = general.get_ctx_token()
    return_values = util.version_overview()
    general.remove_and_refresh_session(session_token)
    return return_values, 200


@app.get("/has_updates")
def has_updates(as_html_response: bool = False) -> bool:
    session_token = general.get_ctx_token()
    return_value = util.has_updates()
    general.remove_and_refresh_session(session_token)
    if as_html_response:
        return responses.HTMLResponse(content=str(return_value))
    return return_value, 200


class UpgradeToAWS(BaseModel):
    only_existing: bool
    remove_from_minio: bool
    force_overwrite: bool


# special case since this will not be part of the common (OS) Versioning since OS will use minio
@app.post("/migrate_minio_to_aws")
def migrate_minio_to_aws(request: UpgradeToAWS) -> int:
    from upgrade_logic.pre_redesign.upgrade_from_minio_to_aws import upgrade

    upgrade(request.only_existing, request.remove_from_minio, request.force_overwrite)


@app.post("/helper")
def helper() -> int:
    pass


@app.post("/helper_function")
def helper_function(function_name: str) -> bool:
    session_token = general.get_ctx_token()
    return_value = util.helper_function(function_name)
    general.remove_and_refresh_session(session_token)
    return return_value, 200


@app.put("/config_changed")
def config_changed() -> responses.PlainTextResponse:
    config_handler.refresh_config()
    return responses.PlainTextResponse(status_code=status.HTTP_200_OK)
