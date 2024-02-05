# ---------------------------------- builtin --------------------------------- #
from hashlib import blake2b
from pathlib import Path
from enum import Enum

# -------------------------------- third party ------------------------------- #
import msgspec

# ----------------------------------- local ---------------------------------- #
from gsm.log import panic



# ---------------------------------------------------------------------------- #
#                                 __str__ tools                                #
# ---------------------------------------------------------------------------- #

def gen_padding(level: int) -> str:
    return ("    " * level) + ("- " if level > 0 else "")



# ---------------------------------------------------------------------------- #
#                                    hashing                                   #
# ---------------------------------------------------------------------------- #

_HASH_DIGEST_SIZE = 64 # 64 is the default digest size for blake2b
_HASH_HEX_DIGEST_SIZE = _HASH_DIGEST_SIZE * 2 # we multiply by 2 because each byte is represented by 2 hex characters
HEX_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

def hash_file(path: Path) -> str:

    if not path.exists():
        panic(f"internal error: tried to hash file that does not exist: {path}")
    
    if not path.is_file():
        panic(f"internal error: tried to hash a non-file: {path}")

    hash = blake2b(open(path, 'rb').read(), digest_size=_HASH_DIGEST_SIZE, usedforsecurity=False).hexdigest()

    return hash

def is_valid_hash(hash: str) -> bool:
    
    if len(hash) != _HASH_HEX_DIGEST_SIZE:
        return False
    
    for char in hash:
        if not char in HEX_DIGITS:
            return False
        
    return True


# ---------------------------------------------------------------------------- #
#                            msgspec struct wrapper                            #
# ---------------------------------------------------------------------------- #

class GsmFileStruct(msgspec.Struct, forbid_unknown_fields=True):
    """
    This class provides a single source of truth for all the msgspec structs used in the project.
    The configurations that shall be used by all structs should be set here.
    """


# ---------------------------------------------------------------------------- #
#                                    version                                   #
# ---------------------------------------------------------------------------- #
    
class VersionType(Enum):
    Semver = "semver"
    Tag = "tag"
    Branch = "branch"
    Commit = "commit"
