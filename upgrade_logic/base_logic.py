from typing import List
from .business_objects import general, neural_search


# if a new business object file is introduced it needes to be added here
__lookup_upgrade_bo = {"general": general, "neural_search": neural_search}


def loop_functions_between_version(
    bussiness_object: str, current_version: str, target_version: str
):
    bo_functions = {}
    for key in __lookup_upgrade_bo:
        for function_name in dir(__lookup_upgrade_bo[key]):
            if function_name.startswith(bussiness_object):
                bo_functions[function_name] = getattr(
                    __lookup_upgrade_bo[key], function_name
                )

    for function_name in bo_functions:
        function_version = ".".join(function_name.split("_")[-3:])
        if __function_is_relevant(function_version, current_version, target_version):
            print("found updatelogic for " + function_name, flush=True)
            func = bo_functions[function_name]
            success = func()
            if not success:
                print(
                    "something went wrong with the update of " + function_name,
                    flush=True,
                )


def __function_is_relevant(
    function_version: str, current_version: str, target_version: str
) -> bool:
    fc = is_newer(function_version, current_version)
    ft = is_newer(function_version, target_version)
    ct = is_newer(current_version, target_version)

    if ct:
        print(
            "current version is newer than target version --> shoudn't happen --> skipped"
        )
        return False
    if fc and not ft:
        return True
    return False


# v1 newer than v2 (e.g. 1.1.2 > 1.1.1)
def is_newer(v1: str, v2: str) -> bool:
    a = [int(x) for x in v1.split(".")]
    b = [int(x) for x in v2.split(".")]
    if len(a) != len(b) and len(a) != 3:
        raise Exception("invalid version format")
    return __is_newer_int(a, b)


def __is_newer_int(v1: List[int], v2: List[int]) -> bool:
    for idx, _ in enumerate(v1):
        if v2[idx] > v1[idx]:
            return False
        elif v2[idx] < v1[idx]:
            return True
    return False
