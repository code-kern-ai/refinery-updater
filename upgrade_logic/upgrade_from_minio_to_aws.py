import typing
import db
from submodules.s3 import controller as s3
import re


def upgrade(only_existing:bool, remove_from_minio:bool, force_overwrite:bool):
    print("upgrade from minio to aws as s3 storage...")
    print(f"options:only_existing = {only_existing} & remove_from_minio = {remove_from_minio} & force_overwrite = {force_overwrite}...")
        
    __upgrade_to_minio(only_existing, remove_from_minio, force_overwrite)
    
    print("upgrade done")
    

def __upgrade_to_minio(only_existing:bool, remove_from_minio:bool, force_overwrite:bool):
    orgs = db.get_all_organization_ids()
    all_buckets = s3.get_all_buckets()
    for bucket in all_buckets:
        if only_existing and not __is_organization_bucket(orgs,bucket):
            continue
        print(f"transferring bucket {bucket} ...")
        s3.transfer_bucket_from_minio_to_aws(bucket,remove_from_minio,force_overwrite)
        print(f"bucket {bucket} done")
    

def __is_organization_bucket(orgs:typing.Dict[str, typing.List[str]],bucket_name:str)->bool:
    if bucket_name in orgs:
        return True
    return False
