from typing import List, Dict, Optional, Tuple

from fastapi import FastAPI
from pydantic import BaseModel
import util

app = FastAPI()


class Request(BaseModel):
    current_version: str
    target_version: str


@app.post("/update_to_version")
def update_to_version(request: Request) -> int:
    return util.upgrade_to_version(request.current_version, request.target_version), ""


class UpgradeToAWS(BaseModel):
    only_existing:bool
    remove_from_minio: bool
    force_overwrite: bool

#special case since this will not be part of the common (OS) Versioning since OS will use minio
@app.post("/migrate_minio_to_aws")
def migrate_minio_to_aws(request:UpgradeToAWS)-> int:
    from upgrade_logic.upgrade_from_minio_to_aws import upgrade
    upgrade(request.only_existing,request.remove_from_minio,request.force_overwrite)


@app.post("/helper")
def helper() -> int:
    from submodules.s3 import controller as s3
    s3.empty_storage(True,True) 
