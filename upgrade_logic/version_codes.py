from enum import Enum


class Version(Enum):
    v0_4 = "v0_4"
    v0_4_1 = "v0_4_1"
    v0_5 = "v0_5"
    v0_6 = "v0_6"
    v1 = "v1"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def from_str(version_str: str):

        version_str = version_str.lower()
        if version_str[0] != "v":
            version_str = "v" + version_str
        version_str = version_str.replace(".", "_")
        try:
            return Version[version_str]
        except:
            return Version.UNKNOWN
