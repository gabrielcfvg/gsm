
# ---------------------------------- builtin --------------------------------- #
from typing import Optional
from pathlib import Path

# -------------------------------- third party ------------------------------- #
import msgspec

# ----------------------------------- local ---------------------------------- #
from gsm.project_files.version import Version, VersionType, SemverVersion, BranchVersion, TagVersion, CommitVersion
from gsm.project_files._files_impl_utils import GsmFileStruct
import gsm.project_files.files as out
from gsm.project_files.hash import is_valid_hash
from gsm.log import info, panic
from gsm.version import GSM_VERSION, parse_version, Semver



LOCK_FILE_PATH = Path("gsm.lock")


class LockFileVersion(GsmFileStruct):
    version_type: VersionType
    version: Optional[str]
    branch: Optional[str]
    tag: Optional[str]
    commit: Optional[str]
    branch_commit: Optional[str]

    def validate(self):

        info(f"validating lock file version")

        # validate the version field
        match self.version_type:

            case VersionType.Semver:
                if self.version == None or parse_version(self.version) == None:
                    panic(f"internal error or corrupted lock file, version not set or invalid semver version string")

            case VersionType.Branch:
                
                if self.branch == None or self.branch == "":
                    panic(f"internal error or corrupted lock file, branch version string is empty")

                # if the version type is branch, the branch_commit field should be set
                if self.branch_commit == None or self.branch_commit == "":
                    panic(f"internal error or corrupted lock file, branch_commit string is empty or not set")

            case VersionType.Tag:
                if self.tag == None or self.tag == "":
                    panic(f"internal error or corrupted lock file, tag version string is empty or not set")

            case VersionType.Commit:
                if self.commit == None or self.commit == "":
                    panic(f"internal error or corrupted lock file, commit version string is empty or not set")
                

    def get_version(self) -> Version:
        
        match self.version_type:
            
            case VersionType.Semver:
                assert self.version != None
                version_semver = parse_version(self.version)
                assert version_semver != None
                return SemverVersion(version_semver)
            
            case VersionType.Branch:
                assert self.branch != None
                return BranchVersion(self.branch, self.branch_commit)
            
            case VersionType.Tag:
                assert self.tag != None
                return TagVersion(self.tag)
            
            case VersionType.Commit:
                assert self.commit != None
                return CommitVersion(self.commit)


class LockFile_Lock(LockFileVersion):
    path: str
    hash: str
    
    def gen_out(self) -> out.LockFile_Lock:

        # validate before generating
        self.validate()

        info(f"generating lock file lock definitive object from the parsing object")

        return out.LockFile_Lock(
            path=Path(self.path),
            hash=self.hash,
            version=self.get_version(),
        )

    def validate(self):

        info(f"validating lock file dependency: {self.path}")
        
        # check if the path isn't a empty string
        if self.path == "":
            panic(f"internal error or lock file corruption: dependency path is empty")

        # we do not need to check if 'path' is a valid path string since any string is a valid path
        # if the string is invalid in any way, the 'Path' constructor would catch it
        if Path(self.path).is_relative_to(Path(".")) == False:
            panic(f"internal error or lock file corruption: dependency path is not relative to the project root, dependency: '{self.path}'")

        # check if the path is relative to the project root
        # we should not check if the lock path directory exists since is possible that no installation has been made since the lock file as updated
        
        # check if the hash string is a valid hash digest
        if is_valid_hash(self.hash) == False:
            panic(f"internal error or lock file corruption: dependency hash is not a valid hash digest, dependency: '{self.path}', hash: '{self.hash}'")

        # validate the version
        super().validate()


class LockFile(GsmFileStruct):
    gsm_version: str
    locks: list[LockFile_Lock]

    def gen_out(self) -> out.LockFile:

        # validate before generating
        self.validate()

        info(f"generating lock file definitive object from the parsing object")

        gsm_version_semver = parse_version(self.gsm_version)
        assert gsm_version_semver != None

        return out.LockFile(
            gsm_version=gsm_version_semver,
            locks=[lock.gen_out() for lock in self.locks],
        )

    def validate(self):

        info(f"performing lock file syntactic validation")

        # since the lock file is generated by gsm, we need to check if the gsm version that generated it is compatible with the current gsm version
        # if the versions are not compatible, is not guaranteed that the values hold the same invariants
        file_gsm_version: Semver = version if (version := parse_version(self.gsm_version)) != None else panic(f"lock file has invalid gsm version string: {self.gsm_version}")
        if file_gsm_version.is_compatible_with(GSM_VERSION) == False:
            panic(
                f"the lock file is not compatible with this version of gsm, consider deleting the lock so that a new lock is generated or use an older version of gsm."
                f"lock file gsm version: {self.gsm_version}, current gsm version: {GSM_VERSION}"
            )


def load_lock_file() -> Optional[out.LockFile]:

    info(f"loading lock file: {LOCK_FILE_PATH}")

    if not LOCK_FILE_PATH.exists():
        info("lock file does not exist")
        return None

    if not LOCK_FILE_PATH.is_file():
        panic(f"the lock file should be a file, but it is not: {LOCK_FILE_PATH}")

    file_content: str = open(LOCK_FILE_PATH, 'r').read()

    try:
        project_lock: LockFile = msgspec.toml.decode(file_content, type=LockFile)
    except msgspec.ValidationError as error:
        panic(f"invalid {LOCK_FILE_PATH}, {error}")

    return project_lock.gen_out()
