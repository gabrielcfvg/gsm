
# ---------------------------------- builtin --------------------------------- #
from __future__ import annotations
from typing import Optional
from pathlib import Path

# -------------------------------- third party ------------------------------- #
import msgspec

# ----------------------------------- local ---------------------------------- #
from gsm.log import info, panic
from gsm.version import parse_version
from gsm.project_files._files_utils import GsmFileStruct, gen_padding, VersionType



CONFIG_FILE_PATH = Path("gsm.toml")


class ConfigFileVersion(GsmFileStruct):
    version: Optional[str] = None
    branch: Optional[str] = None
    tag: Optional[str] = None
    commit: Optional[str] = None

    def validate(self):

        info(f"validanting config file version")

        field = [self.version, self.branch, self.tag, self.commit]
        definition_count = len(field) - field.count(None)

        # check if more than one version type is set
        if definition_count > 1:
            panic(f"invalid {CONFIG_FILE_PATH}, more than one version type is set, only one is allowed")

        # check if no version type is set
        if definition_count == 0:
            panic(f"invalid {CONFIG_FILE_PATH}, no version type is set, one of them is required"
                  f"valid version types: {', '.join(ConfigFileVersion.__dict__.keys())}")
            
        # validade the version field
        match self.get_version_type():

            case VersionType.Semver:
                assert self.version != None
                if parse_version(self.version) == None:
                    panic(f"invalid {CONFIG_FILE_PATH}, invalid semver version string: '{self.version}'")
            
            case VersionType.Branch:
                assert self.branch != None
                if self.branch == "":
                    panic(f"invalid {CONFIG_FILE_PATH}, branch version string is empty")
            
            case VersionType.Tag:
                assert self.tag != None
                if self.tag == "":
                    panic(f"invalid {CONFIG_FILE_PATH}, tag version string is empty")
            
            case VersionType.Commit:
                assert self.commit != None
                if self.commit == "":
                    panic(f"invalid {CONFIG_FILE_PATH}, commit version string is empty")
        
    def get_version_type(self) -> VersionType:
    
        if self.version != None:
            return VersionType.Semver
        elif self.branch != None:
            return VersionType.Branch
        elif self.tag != None:
            return VersionType.Tag
        elif self.commit != None:
            return VersionType.Commit
        else:
            panic(f"internal error: invalid ConfigFileVersion, all version fields are None")

    def get_version(self) -> str:

        match self.get_version_type():

            case VersionType.Semver:
                assert self.version != None
                return self.version
            
            case VersionType.Branch:
                assert self.branch != None
                return self.branch
            
            case VersionType.Tag:
                assert self.tag != None
                return self.tag
            
            case VersionType.Commit:
                assert self.commit != None
                return self.commit

class ConfigFile_Dependency(ConfigFileVersion):
    
    # the members need to be optional because the parent class has fields with default values
    path: Optional[str] = None
    remote: Optional[str] = None

    def validate(self):
        
        info(f"validating config file dependency: {self.path}")
        
        # check if the path is defined
        if self.path == None:
            panic(f"invalid {CONFIG_FILE_PATH}, dependency path is not set")
        
        # check if the remote is defined
        if self.remote == None:
            panic(f"invalid {CONFIG_FILE_PATH}, dependency remote is not set")

        # check if the path is relative
        # we should not check if the directory exists since is possible that no installation has been made since this dependency was added
        # we do not need to check if 'path' is a valid path string since any string is a valid path
        # if the string is invalid in any way, the 'Path' constructor would catch it
        assert Path(self.path).is_relative_to("."), f"invalid {CONFIG_FILE_PATH}, dependency path must always be a path relative to the project root, dependency: '{self.path}'"

        # TODO: maybe we need to check if the dependency path is different from the project root path

        # we can not check if the remote string is a valid url since GitPython do not offer a function to do that
        # if it is invalid, when that value is used, GitPython should raise an exception

        # validate the version
        super().validate()

    def __str__(self, level: int = 0):
        return gen_padding(level) + f"{self.__class__.__name__}(name={self.path}, version_type={self.get_version_type()}, version={self.get_version()}, remote={self.remote})"


class ConfigFile(GsmFileStruct):
    dependencies: list[ConfigFile_Dependency] = msgspec.field(name="dependency")

    def validate(self):

        info(f"validating config file")

        for dependency in self.dependencies:
            dependency.validate()

    def __str__(self, level: int = 0) -> str:
        
        ret = gen_padding(level) + f"{self.__class__.__name__}()"
        for dependency in self.dependencies:
            ret += "\n" + dependency.__str__(level + 1)
        
        return ret


def load_config_file() -> ConfigFile:

    info(f"loading config file: {CONFIG_FILE_PATH}")

    if not CONFIG_FILE_PATH.exists():
        panic(f"{CONFIG_FILE_PATH} does not exist, a config file is required to run gsm.")

    if not CONFIG_FILE_PATH.is_file():
        panic(f"{CONFIG_FILE_PATH} is not a file.")
    
    file_content: str = open(CONFIG_FILE_PATH, 'r').read()
    project_config: ConfigFile = msgspec.toml.decode(file_content, type=ConfigFile)
    project_config.validate()
    
    return project_config
