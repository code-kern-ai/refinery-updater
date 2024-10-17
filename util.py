from datetime import datetime
from upgrade_logic.business_objects import initial_db_version
from typing import Any, List, Dict, Union

from submodules.model.business_objects import app_version, general
from submodules.model.enums import try_parse_enum_value
from service_overview import Service, check_db_uptodate, get_services_info
import git
from upgrade_logic import base_logic


def version_overview() -> List[Dict[str, str]]:
    current_version = app_version.get_all()
    if len(current_version) == 0:
        print(
            "version check before entry add --> update to current version", flush=True
        )
        update_to_newest()

    if not check_db_uptodate():
        print("need to update db", flush=True)
        check_has_newer_version()
        current_version = app_version.get_all()

    lookup_dict = get_services_info(False)
    return [
        {
            "name": lookup_dict[Service[x.service]]["name"],
            "link": lookup_dict[Service[x.service]]["link"],
            "public_repo": lookup_dict[Service[x.service]]["public_repo"],
            "installed_version": check_if_version_exists(
                x.installed_version, x.remote_version, False
            ),
            "remote_version": check_if_version_exists(
                x.installed_version, x.remote_version, True
            ),
            "remote_has_newer": __remote_has_newer(
                x.installed_version, x.remote_version
            ),
            "last_checked": x.last_checked,
        }
        for x in current_version
        if Service.__members__.get(x.service) is not None
    ]


def has_updates() -> bool:
    if not check_db_uptodate():
        print("need to update db", flush=True)
        check_has_newer_version()
    current_version = app_version.get_all()
    return any(
        __remote_has_newer(db_entry.installed_version, db_entry.remote_version)
        for db_entry in current_version
    )


def update_to_newest() -> None:
    something_updated = False
    current_version = app_version.get_all()
    if len(current_version) == 0:
        print(
            "No version found in database -> assuming new installation or version < 1.2.0",
            flush=True,
        )
        initial_db_version.upgrade()
        something_updated = True
        current_version = app_version.get_all()
    if not check_db_uptodate():
        print("checking remote", flush=True)
        check_has_newer_version()
        current_version = app_version.get_all()
    for db_entry in current_version:
        if __remote_has_newer(db_entry.installed_version, db_entry.remote_version):
            base_logic.loop_functions_between_version(
                db_entry.service.lower(),
                db_entry.installed_version,
                db_entry.remote_version,
            )
            # version is overwritten in alfred start up procedure
            db_entry.installed_version = db_entry.remote_version
            something_updated = True
    if something_updated:
        general.commit()
    return something_updated


def check_has_newer_version() -> bool:
    current_version = app_version.get_all()
    if len(current_version) == 0:
        print("version check before entry add --> shouldn't happen", flush=True)
        return False
    lookup_dict = get_services_info(True)
    diff_version = False
    for db_entry in current_version:
        x = try_parse_enum_value(db_entry.service, Service, False)
        if x in lookup_dict:
            link = lookup_dict[x]["link"]
            remote_version = __last_tag(link)
            db_entry.last_checked = datetime.now()
            db_entry.remote_version = remote_version
            if __remote_has_newer(db_entry.installed_version, remote_version):
                diff_version = True
                print(
                    "newer version found for "
                    + db_entry.service
                    + " (used: "
                    + db_entry.installed_version
                    + ", remote: "
                    + remote_version
                    + ")"
                )

    general.commit()
    return diff_version


def __last_tag(repo_link: str) -> Any:
    try:
        g = git.cmd.Git()
        blob = g.ls_remote(repo_link, sort="-v:refname", tags=True)
        if len(blob) == 0:
            return "0.0.0"
        tag = blob.split("\n")[0].split("/")[-1]
        if tag[0] == "v":
            return tag[1:]
        return tag
    except Exception:
        return "0.0.0"


def __remote_has_newer(installed: str, remote: Union[str, None]) -> bool:
    if remote is None:
        return None

    return base_logic.is_newer(remote, installed)


def helper_function(function_name: str) -> bool:
    return base_logic.call_function_by_name(function_name)


def update_versions_to_newest() -> None:
    base_logic.update_versions_to_newest()


def check_if_version_exists(installed: str, remote: str, is_remote: bool) -> str:
    if "0.0.0" in [installed, remote]:
        return "unknown"
    if is_remote:
        return remote
    else:
        return installed
