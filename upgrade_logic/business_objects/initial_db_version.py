from service_overview import get_services_info
from submodules.model.models import AppVersion
from submodules.model.business_objects import app_version, general


def upgrade() -> None:
    print("add service entries...")
    __add_services_to_db(True)
    print("upgrade done")


def __add_services_to_db(only_os: bool) -> None:
    entries = get_services_info(only_os)
    general.add_all(
        [
            AppVersion(service=entries[k]["key"], installed_version="1.2.0")
            for k in entries
        ],
        True,
    )
