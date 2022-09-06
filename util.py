from datetime import datetime
from upgrade_logic.business_objects import initial_db_version
from typing import Any, List, Dict, Union

from submodules.model.business_objects import app_version, general
from service_overview import Service, check_db_uptodate, get_services_info
import git
from upgrade_logic import base_logic


def version_overview() -> List[Dict[str, str]]:
    current_version = app_version.get_all()
    if len(current_version) == 0:
        print("version check before entry add --> shouldn't happen", flush=True)
        return None

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
            "installed_version": x.installed_version,
            "remote_version": x.remote_version,
            "remote_has_newer": __remote_has_newer(
                x.installed_version, x.remote_version
            ),
            "last_checked": x.last_checked,
        }
        for x in current_version
    ]


def update_to_newest() -> None:
    something_updated = False
    current_version = app_version.get_all()
    if len(current_version) == 0:
        print("No version found in database -> assuming < 1.2.0", flush=True)
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
        x = Service[db_entry.service]
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
    g = git.cmd.Git()
    blob = g.ls_remote(repo_link, sort="-v:refname", tags=True)
    tag = blob.split("\n")[0].split("/")[-1]
    if tag[0] == "v":
        return tag[1:]
    return tag


def __remote_has_newer(installed: str, remote: Union[str, None]) -> bool:
    if remote is None:
        return None

    return base_logic.is_newer(remote, installed)
