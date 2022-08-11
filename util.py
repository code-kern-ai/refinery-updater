from upgrade_logic.version_codes import Version
from upgrade_logic import version_v1 as v1
from upgrade_logic import version_v1_1 as v1_1


def upgrade_to_version(current_version: str, target_version: str):
    current_version = Version.from_str(current_version)
    target_version = Version.from_str(target_version)

    if current_version == Version.UNKNOWN or target_version == Version.UNKNOWN:
        print("Can't parse version code -- abort")
        return 400  # Bad Request
    if current_version not in __version_codes or target_version not in __version_codes:
        print("Can't match version code -- abort")
        return 404  # Not found
    if current_version == target_version:
        print("current = target --> no upgrade needed")
        return 405  # method not allowed

    now_upgrading = False
    for version in __version_codes:
        if not now_upgrading and version != current_version:
            # skip till we are at the current version
            continue
        if version == current_version:
            now_upgrading = True
        else:
            __upgrade_to(version)
        if version == target_version:
            break

    return 200


def __upgrade_to(version: Version):
    print("upgrade to:", version.value)
    if version == Version.v0_4:
        print("Nothing to do here...")
    if version == Version.v0_4_1:
        print("Nothing to do here...")
    if version == Version.v0_5:
        print("Nothing to do here...")
    if version == Version.v0_6:
        print("Nothing to do here...")
    if version == Version.v1:
        v1.upgrade()
    if version == Version.v1_1:
        v1_1.upgrade()


__version_codes = [Version.v0_4, Version.v0_4_1, Version.v0_5, Version.v0_6, Version.v1, Version.v1_1]
