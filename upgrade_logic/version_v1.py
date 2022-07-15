import typing
import db
from submodules.s3 import controller as s3
import re


def upgrade():
    print("upgrade to organization buckets...")
    did_something = __upgrade_to_organization_buckets()
    if did_something:
        print("upgrade done")
    else:
        print("nothing was changed, did you already run the update?")
    


def __upgrade_to_organization_buckets()->bool:
    did_something = False
    orgs = db.get_all_organization_ids()
    all_buckets = s3.get_all_buckets()
    for bucket in all_buckets:
        if not __is_bucket_uuid(bucket):
            continue
        if __is_organization_bucket(orgs,bucket):
            continue
        project_id = bucket
        target_bucket = __get_organization_bucket(orgs,project_id)
        if not s3.bucket_exists(target_bucket):
            s3.create_bucket(target_bucket)
        
        bucket_objects = s3.get_bucket_objects(bucket)
        for object in bucket_objects:
            new_object_name = project_id+"/"+object
            if not s3.object_exists(target_bucket,new_object_name):
                s3.copy_object(bucket,object,target_bucket,new_object_name)
            s3.delete_object(bucket,object)
        
        s3.remove_bucket(bucket)
        did_something = True
    return did_something


def __is_organization_bucket(orgs:typing.Dict[str, typing.List[str]],bucket_name:str)->bool:
    if bucket_name in orgs:
        return True
    return False

def __is_bucket_uuid(bucket_name:str)->bool:
    if re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", bucket_name):
        return True
    return False

def __get_organization_bucket(orgs:typing.Dict[str, typing.List[str]],project_bucket_name:str)->typing.Any:

    for org in orgs:
        if project_bucket_name in orgs[org]:
            return org
    
    # no organization found, old project --> use "archive" bucket
    return "archive"

