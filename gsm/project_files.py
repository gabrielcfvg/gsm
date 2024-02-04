assert __name__ != "__main__"

from typing import List, Optional
import msgspec
from pathlib import Path
from log import panic


class GsmStruct(msgspec.Struct, forbid_unknown_fields=True): pass



class Dependency(GsmStruct):
    path: str
    remote: str
    semver_version: Optional[str] = None
    raw_version: Optional[str] = None

    def validate(self):
        # TODO: unimplemented
        pass

    def get_version(self) -> str:

        if self.semver_version != None:
            return self.semver_version
        elif self.raw_version != None:
            return self.raw_version
        else:
            panic("dependency has no version")

    def __str__(self, level: int = 0):
        return "    " * level + f"Dependency(name={self.path}, version={self.get_version()}, remote={self.remote})\n"

class ProjectConfig(GsmStruct):
    dependencies: List[Dependency] = msgspec.field(name="dependency")

    def validate(self):
        # TODO: unimplemented
        pass

    def __str__(self, level: int = 0) -> str:
        
        ret = "    " * level + f"ProjectConfig()\n"
        for dependency in self.dependencies:
            ret += dependency.__str__(level + 1)
        
        return ret




def load_project_config(path: Path) -> ProjectConfig:

    assert path.exists()
    
    file_content: str = open(path, 'r').read()
    project_config: ProjectConfig = msgspec.toml.decode(file_content, type=ProjectConfig)
    project_config.validate()
    
    return project_config



class DependencyLock(GsmStruct):
    path: str
    hash: str
    ref_name: str
    
    def validate(self):
        # TODO: unimplemented
        pass

    def __str__(self, level: int = 0) -> str:
        return "    " * level + f"DependencyLock(name={self.path}, ref_name={self.ref_name}, hash={self.hash})\n"

class ProjectLock(GsmStruct):
    dependencies: List[DependencyLock]

    def validate(self):
        # TODO: unimplemented
        pass

    def __str__(self, level: int = 0) -> str:
        
        ret = "    " * level + f"ProjectLock()\n"
        for lock in self.dependencies:
            ret += lock.__str__(level + 1)
        
        return ret


def load_project_lock_file(path: Path) -> ProjectLock:

    assert path.exists()

    file_content: str = open(path, 'r').read()
    project_lock: ProjectLock = msgspec.toml.decode(file_content, type=ProjectLock)
    project_lock.validate()

    return project_lock

