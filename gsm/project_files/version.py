# ---------------------------------- builtin --------------------------------- #
from dataclasses import dataclass
from typing import Protocol, Optional, override
from enum import Enum
from abc import abstractmethod

# ----------------------------------- local ---------------------------------- #
from gsm.semver import Semver



class VersionType(Enum):
    Semver = "semver"
    Tag = "tag"
    Branch = "branch"
    Commit = "commit"


class VersionVisitor(Protocol):

    @abstractmethod
    def visit_semver(self, version: Semver): ...

    @abstractmethod
    def visit_tag(self, tag: str): ...

    @abstractmethod
    def visit_branch(self, branch: str): ...

    @abstractmethod
    def visit_commit(self, commit: str): ...


class Version(Protocol):

    @abstractmethod
    def accept(self, visitor: VersionVisitor): ...

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...


@dataclass
class SemverVersion(Version):
    version: Semver

    def accept(self, visitor: VersionVisitor):
        return visitor.visit_semver(self.version)
    
    @override
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, SemverVersion):
            return False
        
        return self.version == other.version


@dataclass
class TagVersion(Version):
    tag: str

    def accept(self, visitor: VersionVisitor):
        return visitor.visit_tag(self.tag)

    @override
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, TagVersion):
            return False
        
        return self.tag == other.tag
        

@dataclass
class BranchVersion(Version):
    branch: str
    commit: Optional[str] = None # commit lock for the lock file

    def accept(self, visitor: VersionVisitor):
        return visitor.visit_branch(self.branch)
    
    @override
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, BranchVersion):
            return False
        
        return self.branch == other.branch


@dataclass
class CommitVersion(Version):
    commit: str

    def accept(self, visitor: VersionVisitor):
        return visitor.visit_commit(self.commit)
    
    @override
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, CommitVersion):
            return False
        
        return self.commit == other.commit


def get_version_type(version: Version) -> VersionType:
    
    version_type: Optional[VersionType] = None

    class VersionTypeVisitor(VersionVisitor):

        @override
        def visit_semver(self, version: Semver):
            nonlocal version_type
            version_type = VersionType.Semver

        @override
        def visit_tag(self, tag: str):
            nonlocal version_type
            version_type = VersionType.Tag

        @override
        def visit_branch(self, branch: str):
            nonlocal version_type
            version_type = VersionType.Branch

        @override
        def visit_commit(self, commit: str):
            nonlocal version_type
            version_type = VersionType.Commit

    version.accept(VersionTypeVisitor())
    assert version_type != None

    return version_type
