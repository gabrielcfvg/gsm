
# ---------------------------------- builtin --------------------------------- #
from __future__ import annotations
import re
from typing import Optional, cast
import enum



# TODO: support full SemVer: 
# https://semver.org/#semantic-versioning-specification-semver
# 
# tasks:
# 
# - suportar parsing de versões com pré-release
#   - ex: 1.0.0-alpha, 1.0.0-alpha.1, 1.0.0-0.3.7, 1.0.0-x.7.z.92
# 
# - suportar parsing de versões com metadados de build
#   - ex: 1.0.0+20130313144700, 1.0.0-beta+exp.sha.5114f85
#   - obs: versões de pré-release e metadados de build podem compartilhar a mesma
#          sintaxe de identificadores
# 
# - suportar versões de pré-release
# - suportar versões com metadados de build
# 
# - TODO: mostar warning para o usuário caso versões com metadados de build
#   sejam usados no modo SemVer


# TODO: write a more readable regex
VERSION_REGEX = re.compile(r"^(?P<major>0|[1-9]\d*)(?:\.(?P<minor>0|[1-9]\d*)(?:\.(?P<patch>0|[1-9]\d*))?)?(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")

class _IdentifierSequence:
    items: list[int | str]

    def __init__(self, *items: int | str):

        for item in items:
            if isinstance(item, str) and not self._is_valid_identifier(item):
                raise RuntimeError(f"invalid non-numeric identifier: {item}")
            elif isinstance(item, int) and item < 0:
                raise RuntimeError(f"invalid numeric identifier: {item}")

        self.items = list(items)

    @classmethod
    def _is_valid_identifier(cls, idt: str) -> bool:
        
        if not idt.isascii():
            return False
        
        return idt.replace("-", "").isalnum()

    @classmethod
    def _identifier_gt(cls, idt1: int | str, idt2: int | str) -> bool:

        # numeric identifiers always have lower precedence than non-numeric.
        # if they don't have the same type, the non-numeric is greater
        if type(idt1) != type(idt2):
            return type(idt1) == str
        
        # numeric identifiers are compared numerically
        if isinstance(idt1, int):
            assert isinstance(idt2, int)    
            return idt1 > idt2
        
        assert isinstance(idt1, str)
        assert isinstance(idt2, str)
        return cls._non_numeric_identifier_gt(idt1, idt2)
    
    @classmethod
    def _non_numeric_identifier_gt(cls, idt1: str, idt2: str) -> bool:
        
        # non-numeric identifiers are compared lexicographically
        assert cls._is_valid_identifier(idt1) and cls._is_valid_identifier(idt2)
        idt_list = [idt1, idt2]
        idt_list.sort()
        return idt_list[0] == idt1
        
    def __eq__(self, other: object) -> bool:
            
        if not isinstance(other, _IdentifierSequence):
            return False
            
        return self.items == other.items    
    
    def __gt__(self, other: object) -> bool:

        assert isinstance(other, _IdentifierSequence), f"comparison is not supported with types other than {self.__class__.__name__}"

        # the precedence is determined by the first difference.
        smallest_len = min(len(self.items), len(other.items))
        for i in range(0, smallest_len):
            if self.items[i] != other.items[i]:
                return self._identifier_gt(self.items[i], other.items[i])
            
        # if no difference is found, the longer sequence is considered greater
        return len(self.items) > len(other.items)

    def __ne__(self, other: object) -> bool:
        return not (self == other)
    
    def __lt__(self, other: object) -> bool:
        return not (self == other) and not (self > other)
    
    def __ge__(self, other: object) -> bool:
        return (self == other) or (self > other)
    
    def __le__(self, other: object) -> bool:
        return (self == other) or (self < other)
                
                
class Semver:
    _core: _IdentifierSequence

    # ---------------------------------- public ---------------------------------- #

    def __init__(self, core: list[int]):

        if len(core) == 0:
            raise RuntimeError("version core must have at least the major number")
        
        # we don't need to check if the core version is valid, because the
        # constructor of _IdentifierSequence already does that
        self._core = _IdentifierSequence(*core)

    def is_compatible_with(self, other: Semver) -> bool:
        
        self_major = self._core.items[0]
        other_major = other._core.items[0]

        if self_major != other_major:
            return False

        if self_major == 0:
            return self == other
        
        return other >= self

    def to_string(self) -> str:

        core_str = ".".join(map(str, self._core.items))
        return f"{core_str}"
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"Semver({self.to_string()})"


    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Semver):
            return False
        
        not_eq = False
        not_eq |= self._core != other._core

        return not not_eq
    
    def __gt__(self, other: object) -> bool:
        assert isinstance(other, Semver), f"comparison is not supported with type {type(other)}"
        return self._core > other._core

    def __ne__(self, other: object):
        return not (self == other)
        
    def __ge__(self, other: object):
        return (self == other) or (self > other)
    
    def __lt__(self, other: object):
        return (not (self == other)) and (not (self > other))
    
    def __le__(self, other: object):
        return (self == other) or (self < other)
    

    def __hash__(self):

        major = self._core.items[0] if len(self._core.items) > 0 else 0
        minor = self._core.items[1] if len(self._core.items) > 1 else 0
        patch = self._core.items[2] if len(self._core.items) > 2 else 0

        return hash((major, minor, patch))
    
    # ---------------------------------- private --------------------------------- #

    def _core_lenght(self) -> int:
        return len(self._core.items)

    def _validate(self):
        assert len(self._core.items) > 0
        for item in self._core.items:
            assert type(item) == int

    def _major(self) -> int:
        self._validate()
        return cast(int, self._core.items[0])
    
    def _minor(self) -> int:
        self._validate()
        assert len(self._core.items) > 1
        return cast(int, self._core.items[1])
    
    def _patch(self) -> int:
        self._validate()
        assert len(self._core.items) > 2
        return cast(int, self._core.items[2])    


# ---------------------------------------------------------------------------- #
#                                version parsing                               #
# ---------------------------------------------------------------------------- #

class VersionParseErrorType(enum.Enum):
    PRE_RELEASE_NOT_SUPORTED = enum.auto()
    BUILD_METADATA_NOT_SUPORTED = enum.auto()

class VersionParseError(Exception):
    error_type: VersionParseErrorType

    def __init__(self, error_type: VersionParseErrorType):
        super().__init__(self.get_message(error_type))
        self.error_type = error_type

    @staticmethod
    def get_message(error_type: VersionParseErrorType) -> str:
        
        match error_type:
            case VersionParseErrorType.PRE_RELEASE_NOT_SUPORTED:
                return "pre-release is not supported yet"
            case VersionParseErrorType.BUILD_METADATA_NOT_SUPORTED:
                return "build metadata is not supported yet"
    

def _semver_from_match_group(match: re.Match[str]) -> Semver:

    core_list: list[int] = [int(match.group("major"))]

    if (_minor := match.group("minor")) != None:
        core_list.append(int(_minor))

    if (_patch := match.group("patch")) != None:
        core_list.append(int(_patch))

    # pre-release is not supported yet
    if match.group("prerelease") != None:
        raise VersionParseError(VersionParseErrorType.PRE_RELEASE_NOT_SUPORTED)
    
    # build metadata is not supported yet
    if match.group("buildmetadata") != None:
        raise VersionParseError(VersionParseErrorType.BUILD_METADATA_NOT_SUPORTED)

    return Semver(core_list)

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
