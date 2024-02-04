from __future__ import annotations

assert __name__ != "__main__"

import re
from typing import Optional

VERSION_REGEX = re.compile(r"^(0|[1-9]\d*)(\.(0|[1-9]\d*)(\.(0|[1-9]\d*))?)?")

class Semver:
    major: int
    minor: int
    patch: int

    def __init__(self, major: int, minor: int, patch: int):

        for number in [major, minor, patch]:
            if number < 0:
                raise RuntimeError("invalid version number")
            
        self.major = major
        self.minor = minor
        self.patch = patch


    def is_compatible_with(self, other: Semver) -> bool:
        
        return (self.major == other.major) and (other >= self)

    def to_string(self) -> str:

        return f"{self.major}.{self.minor}.{self.patch}"


    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Semver):
            return False
        
        return (self.major == other.major) and (self.minor == other.minor) and (self.patch == other.patch)
    
    def __ne__(self, other: object):
        return not (self == other)
    

    def __gt__(self, other: object) -> bool:
        
        assert isinstance(other, Semver), f"comparison is not supported with type {type(other)}"
    
        if self.major != other.major:
            return self.major > other.major
        
        if self.minor != other.minor:
            return self.minor > other.minor
        
        return self.patch > other.patch
        
    def __ge__(self, other: object):
        return (self == other) or (self > other)
    
    def __lt__(self, other: object):
        return (not (self == other)) and (not (self > other))
    
    def __le__(self, other: object):
        return (self == other) or (self < other)

    


def _semver_from_match_group(match: re.Match[str]) -> Semver:

    major = int(match.group(1))

    minor = 0
    if (_minor := match.group(3)) != None:
        minor = int(_minor)

    patch = 0
    if (_patch := match.group(5)) != None:
        patch = int(_patch)

    return Semver(major, minor, patch)

def parse_version(text: str) -> Optional[Semver]:

    res = VERSION_REGEX.match(text)

    if res == None:
        return None
    
    if res.group(0) != text:
        return None
    
    return _semver_from_match_group(res)

def find_first_version(text: str) -> Optional[Semver]:

    res = VERSION_REGEX.search(text)

    if res == None:
        return None
    
    return _semver_from_match_group(res)

