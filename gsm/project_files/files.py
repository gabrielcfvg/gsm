# ---------------------------------- builtin --------------------------------- #
from pathlib import Path

# ----------------------------------- local ---------------------------------- #
from gsm.version import Semver
from gsm.project_files.version import Version
from gsm.project_files.hash import is_valid_hash


# ---------------------------------------------------------------------------- #
#                                __repr__ tools                                #
# ---------------------------------------------------------------------------- #

def gen_padding(level: int) -> str:
    return ("    " * level) + ("- " if level > 0 else "")


# ---------------------------------------------------------------------------- #
#                                  config file                                 #
# ---------------------------------------------------------------------------- #

class ConfigFile_Dependency:
    path: Path
    remote: str
    version: Version

    def __init__(self, path: Path, remote: str, version: Version):
        
        assert path.is_relative_to(Path("."))
        assert len(remote) > 0
        
        self.path = path
        self.remote = remote
        self.version = version

    def __repr__(self, level: int = 0) -> str:
        
        padding = gen_padding(level)
        return f"{padding}Dependency(path: {self.path}, remote: {self.remote}, version: {self.version})"


class ConfigFile:
    dependencies: list[ConfigFile_Dependency]

    def __init__(self, dependencies: list[ConfigFile_Dependency]):
        self.dependencies = dependencies

    def __repr__(self, level: int = 0) -> str:
        
        padding = gen_padding(level)
        repr = f"{padding}ConfigFile()"
        
        for dependency in self.dependencies:
            repr += "\n" + dependency.__repr__(level + 1)

        return repr


# ---------------------------------------------------------------------------- #
#                                   lock file                                  #
# ---------------------------------------------------------------------------- #

class LockFile_Lock:
    path: Path # path to the folder where the dependency is stored
    hash: str # hash of the dependency tree in the locked version
    version: Version # dependency locked version
    
    # we do not need to store the remote url since it is stored in the config file.
    # if the config file remote change, we will know by the hash of the mirror

    def __init__(self, path: Path, hash: str, version: Version):
        
        assert path.is_relative_to(Path("."))
        assert is_valid_hash(hash)

        self.path = path
        self.hash = hash
        self.version = version

    def __repr__(self, level: int = 0) -> str:

        padding = gen_padding(level)
        return f"{padding}Lock(path: {self.path}, hash: {self.hash}, version: {self.version})"


class LockFile:
    gsm_version: Semver # version of gsm that generated the lock file
    locks: list[LockFile_Lock]

    def __init__(self, gsm_version: Semver, locks: list[LockFile_Lock]):
        self.gsm_version = gsm_version
        self.locks = locks

    def __repr__(self, level: int = 0) -> str:
            
        padding = gen_padding(level)
        repr = f"{padding}LockFile(gsm_version: {self.gsm_version})"
        
        for lock in self.locks:
            repr += "\n" + lock.__repr__(level + 1)

        return repr

# ---------------------------------------------------------------------------- #
#                                 mirrors file                                 #
# ---------------------------------------------------------------------------- #

# TODO: We can use a hex representation of the remote url for generating the
#       filename of the mirror object files

class MirrorsFile_Mirror:
    remote: str

    def __init__(self, remote: str):
            
        assert len(remote) > 0
        self.remote = remote

    def __repr__(self, level: int = 0) -> str:
            
        padding = gen_padding(level)
        return f"{padding}Mirror(remote: {self.remote})"


class MirrorsFile:
    gsm_version: Semver # version of gsm that generated the mirrors file
    mirrors: list[MirrorsFile_Mirror]

    def __init__(self, gsm_version: Semver, mirrors: list[MirrorsFile_Mirror]):
        self.gsm_version = gsm_version
        self.mirrors = mirrors

    def __repr__(self, level: int = 0) -> str:
                
        padding = gen_padding(level)
        repr = f"{padding}MirrorsFile(gsm_version: {self.gsm_version})"
        
        for mirror in self.mirrors:
            repr += "\n" + mirror.__repr__(level + 1)

        return repr
