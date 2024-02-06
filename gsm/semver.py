
# ---------------------------------- builtin --------------------------------- #
from __future__ import annotations
import re
from typing import Optional, cast



# TODO: support full SemVer: 
# https://semver.org/#semantic-versioning-specification-semver
# 
# alteraçoes a fazer:
# 
# - suportar versões de pré-release
#   ex: 1.0.0-alpha, 1.0.0-alpha.1, 1.0.0-0.3.7, 1.0.0-x.7.z.92
# 
# - suportar metadados de build
#   ex: 1.0.0+20130313144700, 1.0.0-beta+exp.sha.5114f85
# 
# - versões de pré-release e metadados de build podem compartilhar a mesma
#   sintaxe de identificadores
# 
# - metadados de build não devem ser consideradas na comparação
# 
# - TODO: mostar warning para o usuário caso versões com metadados de build
#   sejam usados no modo SemVer


# _VERSION_IDENTIFIER = r""
VERSION_REGEX = re.compile(r"^(0|[1-9]\d*)(\.(0|[1-9]\d*)(\.(0|[1-9]\d*))?)?")

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
    _pre_release: _IdentifierSequence
    # TODO: build metadata

    # ---------------------------------- public ---------------------------------- #

    def __init__(self, core: list[int], pre_release: list[int | str] = []):

        if len(core) == 0:
            raise RuntimeError("version core must have at least the major number")
        
        # we don't need to check if the core version is valid, because the
        # constructor of _IdentifierSequence already does that
        self._core = _IdentifierSequence(*core)
        self._pre_release = _IdentifierSequence(*pre_release)

    def is_compatible_with(self, other: Semver) -> bool:
        
        self_major = self._core.items[0]
        other_major = other._core.items[0]

        if self_major != other_major:
            return False

        if self_major == 0:
            return self == other
        
        # TODO: considerar pre-release

        return other >= self

    def to_string(self) -> str:

        core_str = ".".join(map(str, self._core.items))

        pre_release_str = "-" if len(self._pre_release.items) > 0 else ""
        pre_release_str += ".".join(map(str, self._pre_release.items))

        return f"{core_str}{pre_release_str}"
    
    def __str__(self) -> str:
        return self.to_string()


    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Semver):
            return False
        
        not_eq = False
        not_eq |= self._core != other._core
        # TODO: comparar pre-release

        return not not_eq
    
    def __gt__(self, other: object) -> bool:
        
        # TODO: considerar pre-release
        assert isinstance(other, Semver), f"comparison is not supported with type {type(other)}"
        return self._core > other._core

    def __ne__(self, other: object):
        # TODO: considerar pre-release
        return not (self == other)
        
    def __ge__(self, other: object):
        # TODO: considerar pre-release
        return (self == other) or (self > other)
    
    def __lt__(self, other: object):
        # TODO: considerar pre-release
        return (not (self == other)) and (not (self > other))
    
    def __le__(self, other: object):
        # TODO: considerar pre-release
        return (self == other) or (self < other)
    
    # ---------------------------------- private --------------------------------- #

    def _validate(self):

        assert len(self._core.items) > 0
        for item in self._core.items:
            assert type(item) == int

    def _major(self) -> int:
        assert self._validate()
        return cast(int, self._core.items[0])
    
    def _minor(self) -> int:
        assert self._validate()
        assert len(self._core.items) > 1
        return cast(int, self._core.items[1])
    
    def _patch(self) -> int:
        assert self._validate()
        assert len(self._core.items) > 2
        return cast(int, self._core.items[2])
    
    # def _pre_rel_nth(self, idx: int) -> int | str:
    #     assert idx >= 0
    #     assert self._validate()
    #     assert idx < len(self._pre_release.items)
    #     return self._pre_release.items[idx]


    


def _semver_from_match_group(match: re.Match[str]) -> Semver:

    core_list: list[int] = [int(match.group(1))]

    if (_minor := match.group(3)) != None:
        core_list.append(int(_minor))

    if (_patch := match.group(5)) != None:
        core_list.append(int(_patch))

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

