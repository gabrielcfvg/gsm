# ---------------------------------- builtin --------------------------------- #
import importlib.metadata

# ----------------------------------- local ---------------------------------- #
from semver import Semver, parse_version
from log import panic

GSM_VERSION: Semver = version if (version := parse_version(importlib.metadata.version('gsm'))) != None else panic("invalid version string")
