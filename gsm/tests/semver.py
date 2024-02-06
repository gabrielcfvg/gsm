
# ---------------------------------- builtin --------------------------------- #
import random
from typing import Callable

# -------------------------------- third party ------------------------------- #
import pytest

# ----------------------------------- local ---------------------------------- #
from gsm.semver import *



# ---------------------------------------------------------------------------- #
#                                     utils                                    #
# ---------------------------------------------------------------------------- #

def gen_core_arra                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ngement_with_repetition(
        core_values: set[int], core_gen_null: bool = True,
        always_include: set[int] = set()) -> list[list[int]]:
    
    assert always_include.issubset(core_values)
    output: list[list[int]] = []

    def push(core_list: list[int]):

        for obligatory_item in always_include:
            if obligatory_item not in core_list:
                return
            
        output.append(core_list)

    for major in core_values:

        if core_gen_null:
            push([major])

        for minor in core_values:

            if core_gen_null:
                push([major, minor])

            for patch in core_values:  
                push([major, minor, patch])

    return output


MAX_VERSION_NUMBER = 5

def calc_version_list_size() -> int:
    return (MAX_VERSION_NUMBER ** 3) + (MAX_VERSION_NUMBER ** 2) + MAX_VERSION_NUMBER

def gen_version_list() -> list[Semver]:

    output: list[Semver] = []
    for major in range(0, MAX_VERSION_NUMBER):
        output.append(Semver([major]))
        for minor in range(0, MAX_VERSION_NUMBER):
            output.append(Semver([major, minor]))
            for patch in range(0, MAX_VERSION_NUMBER):
                output.append(Semver([major, minor, patch]))

    assert calc_version_list_size() == len(output)
    return output

@pytest.fixture(scope="module")
def version_samples() -> list[Semver]:

    return gen_version_list()

@pytest.fixture(scope="module")
def random_version_pair_samples() -> list[tuple[Semver, Semver]]:

    list1 = gen_version_list()
    list2 = gen_version_list()
    random.shuffle(list2)

    assert len(list1) == len(list2)
    return [(list1[idx], list2[idx]) for idx in range(0, len(list1))]


# ---------------------------------------------------------------------------- #
#                                     tests                                    #
# ---------------------------------------------------------------------------- #

def test_gen_core_arrangement():

    value_sets = [{i for i in range(0, j)} for j in range(1, 5)]
    for value_set in value_sets:
        assert len(gen_core_arrangement_with_repetition(value_set)) == len(value_set)**3 + len(value_set)**2 + len(value_set)
        assert len(gen_core_arrangement_with_repetition(value_set, core_gen_null=False)) == len(value_set)**3


def test_semver_construction():

    # inputing a core list with no values should raise an error
    with pytest.raises(RuntimeError):
        Semver(core=[])

    # inputing negative values to core list should raise an error
    for core_values in gen_core_arrangement_with_repetition({0, -1}, always_include={-1}):
        with pytest.raises(RuntimeError):
            Semver(core=core_values)

    # TODO: testar requisitos do pre-release

# def test_semver_equality():
# 
#     # TODO: testar a não-equidade das versões com cores nulos
#     # ex: 0.1 != 0.1.0, 0.1.0 > 0.1
# 
#     assert Semver(0, 0, 0) == Semver(0, 0, 0)
#     assert Semver(1, 2, 3) == Semver(1, 2, 3)
# 
#     assert Semver(7, 2, 3) != Semver(1, 2, 3)
#     assert Semver(1, 8, 3) != Semver(1, 2, 3)
#     assert Semver(1, 2, 9) != Semver(1, 2, 3)
# 
#     assert Semver(7, 8, 3) != Semver(1, 2, 3)
#     assert Semver(1, 8, 9) != Semver(1, 2, 3)
#     assert Semver(7, 2, 9) != Semver(1, 2, 3)
# 
#     assert Semver(7, 8, 9) != Semver(1, 2, 3)
# 
# def test_semver_compatibility(random_version_pair_samples: list[tuple[Semver, Semver]]):
# 
#     # TODO: support filters
#     def for_all_pairs(func: Callable[[Semver, Semver], bool]) -> bool:
#         return all(func(v1, v2) for v1, v2 in random_version_pair_samples)
# 
#     # TODO: testar a não-compatibilidade de versões com cores nulos
#     # ex: 0.1 != 0.1.0, 0.1.0 > 0.1
# 
#     # version is always compatible with itself
#     assert Semver(0, 0, 0).is_compatible_with(Semver(0, 0, 0))
#     assert for_all_pairs(lambda v1, v2: v1.is_compatible_with(v1) and v2.is_compatible_with(v2))
# 
#     # version is always incompatible with another with a different major
#     assert Semver(0, 0, 0).is_compatible_with(Semver(1, 0, 0)) == False
#     assert Semver(1, 0, 0).is_compatible_with(Semver(0, 0, 0)) == False
#     assert Semver(0, 0, 0).is_compatible_with(Semver(1, 1, 0)) == False
#     assert Semver(0, 0, 0).is_compatible_with(Semver(1, 0, 1)) == False
#     assert Semver(0, 0, 0).is_compatible_with(Semver(1, 1, 1)) == False
#     assert for_all_pairs(lambda v1, v2: (v1.is_compatible_with(v2) == False) if (v1.major != v2.major) else True)
# 
#     # if the version major is 0, it only is compatible with another version, if
#     # and only if, it is equal to the other version.
#     # in other words, if the major is 0, then the version is only compatible
#     # with itself.
#     assert Semver(0, 0, 0).is_compatible_with(Semver(0, 0, 0))
#     assert Semver(0, 0, 0).is_compatible_with(Semver(0, 0, 1)) == False
#     assert Semver(0, 0, 0).is_compatible_with(Semver(0, 1, 0)) == False
#     assert Semver(0, 0, 0).is_compatible_with(Semver(0, 1, 1)) == False
#     assert for_all_pairs(lambda v1, v2: (v1 == v2) == v1.is_compatible_with(v2) if (v1.major == 0) or (v2.major == 0) else True)
# 
#     # version is only compatible if minor is equal or greater than the other version minor
#     # if the minor is equal, then patch should be equal or greater the other version patch
#     assert Semver(1, 0, 0).is_compatible_with(Semver(1, 0, 0)) # equal
#     assert Semver(1, 0, 0).is_compatible_with(Semver(1, 0, 1)) # patch greater
#     assert Semver(1, 0, 0).is_compatible_with(Semver(1, 1, 0)) # minor greater
#     assert Semver(1, 0, 0).is_compatible_with(Semver(1, 1, 1)) # both greater
#     assert Semver(1, 1, 1).is_compatible_with(Semver(1, 1, 0)) == False # patch smaller
#     assert Semver(1, 1, 1).is_compatible_with(Semver(1, 0, 1)) == False # minor smaller
#     assert Semver(1, 1, 1).is_compatible_with(Semver(1, 0, 0)) == False # both smaller
#     assert Semver(1, 1, 1).is_compatible_with(Semver(1, 0, 2)) == False # minor smaller && patch greater
#     assert Semver(1, 1, 1).is_compatible_with(Semver(1, 2, 0)) # minor greater && patch smaller
#     assert for_all_pairs(lambda v1, v2: v1.is_compatible_with(v2) if (v1.major != 0) and (v2.major != 0) and (v1.major == v2.major) and (v1.minor < v2.minor) else True)
#     assert for_all_pairs(lambda v1, v2: v1.is_compatible_with(v2) if (v1.major != 0) and (v2.major != 0) and (v1.major == v2.major) and (v1.minor == v2.minor) and (v1.patch <= v2.patch) else True)
# 
# def test_semver_ordering(random_version_pair_samples: list[tuple[Semver, Semver]]):
#     
#     def for_all_pairs(func: Callable[[Semver, Semver], bool]) -> bool:
#         return all(func(v1, v2) for v1, v2 in random_version_pair_samples)
# 
#     # TODO: testar a não-equidade das versões com cores nulos
#     # ex: 0.1 != 0.1.0, 0.1.0 > 0.1
# 
#     # any pair of version should be always and exclusively be: equal, greater, or smaller
#     assert Semver(1, 0, 0) > Semver(0, 0, 0)
#     assert not (Semver(1, 0, 0) < Semver(0, 0, 0))
#     assert not (Semver(1, 0, 0) == Semver(0, 0, 0))
#     assert Semver(0, 0, 0) < Semver(1, 0, 0)
#     assert not (Semver(0, 0, 0) > Semver(1, 0, 0))
#     assert not (Semver(0, 0, 0) == Semver(1, 0, 0))
#     assert Semver(0, 0, 0) == Semver(0, 0, 0)
#     assert not (Semver(0, 0, 0) > Semver(0, 0, 0))
#     assert not (Semver(0, 0, 0) < Semver(0, 0, 0))
#     assert for_all_pairs(lambda v1, v2: [(v1 == v2), (v1 > v2), (v1 < v2)].count(True) == 1)
# 
#     # if a version is different from another, they should be greater or smaller than the other one
#     # the inverse shold be also true
#     assert Semver(1, 2, 3) != Semver(3, 2, 1)
#     assert not (Semver(1, 2, 3) > Semver(3, 2, 1))
#     assert Semver(1, 2, 3) < Semver(3, 2, 1)
#     assert for_all_pairs(lambda v1, v2: (v1 != v2) == ((v1 > v2) or (v1 < v2)))
# 
#     # if v1 is greater then v2, then v2 should be always smaller than v1
#     assert (Semver(3, 2, 1) > Semver(1, 2, 3)) == (Semver(1, 2, 3) < Semver(3, 2, 1)) # maior
#     assert (Semver(1, 2, 3) > Semver(3, 2, 1)) == (Semver(3, 2, 1) < Semver(1, 2, 3)) # menor
#     assert (Semver(1, 2, 3) > Semver(1, 2, 3)) == (Semver(1, 2, 3) < Semver(1, 2, 3)) # igual
#     assert for_all_pairs(lambda v1, v2: (v1 > v2) == (v2 < v1))
# 
#     # if v1 is equal-or-greater than v2, then v1 should never be smaller than v2
#     assert (Semver(3, 2, 1) >= Semver(1, 2, 3)) == (not (Semver(3, 2, 1) < Semver(1, 2, 3))) # maior
#     assert (Semver(1, 2, 3) >= Semver(3, 2, 1)) == (not (Semver(1, 2, 3) < Semver(3, 2, 1))) # menor
#     assert (Semver(1, 2, 3) >= Semver(1, 2, 3)) == (not (Semver(1, 2, 3) < Semver(1, 2, 3))) # igual
#     assert for_all_pairs(lambda v1, v2: (v1 >= v2) == (not (v1 < v2)))
# 
#     # if v1 is equal-or-smaller than v2, then v1 should never be greater than v2
#     assert (Semver(3, 2, 1) <= Semver(1, 2, 3)) == (not (Semver(3, 2, 1) > Semver(1, 2, 3))) # maior
#     assert (Semver(1, 2, 3) <= Semver(3, 2, 1)) == (not (Semver(1, 2, 3) > Semver(3, 2, 1))) # menor
#     assert (Semver(1, 2, 3) <= Semver(1, 2, 3)) == (not (Semver(1, 2, 3) > Semver(1, 2, 3))) # igual
#     assert for_all_pairs(lambda v1, v2: (v1 <= v2) == (not (v1 > v2)))
# 
#     # if v1 is equal-or-greater than v2, then v2 should be always equal-or-smaller than v1
#     assert (Semver(3, 2, 1) >= Semver(1, 2, 3)) == (Semver(1, 2, 3) <= Semver(3, 2, 1)) # maior
#     assert (Semver(1, 2, 3) >= Semver(3, 2, 1)) == (Semver(3, 2, 1) <= Semver(1, 2, 3)) # menor
#     assert (Semver(1, 2, 3) >= Semver(1, 2, 3)) == (Semver(1, 2, 3) <= Semver(1, 2, 3)) # igual
#     assert for_all_pairs(lambda v1, v2: (v1 >= v2) == (v2 <= v1))
# 
# 
#     # if the version major is greater than the another version major, then it is always greater
#     assert Semver(1, 0, 0) > Semver(0, 0, 0)
#     assert Semver(1, 0, 0) > Semver(0, 1, 0)
#     assert Semver(1, 0, 0) > Semver(0, 0, 1)
#     assert Semver(1, 0, 0) > Semver(0, 1, 1)
#     assert for_all_pairs(lambda v1, v2: v1 > v2 if v1.major > v2.major else True)
# 
#     # if the version major is smaller, then is is always smaller
#     assert Semver(0, 0, 0) < Semver(1, 0, 0)
#     assert Semver(0, 1, 0) < Semver(1, 0, 0)
#     assert Semver(0, 0, 1) < Semver(1, 0, 0)
#     assert Semver(0, 1, 1) < Semver(1, 0, 0)
#     assert for_all_pairs(lambda v1, v2: v1 < v2 if v1.major < v2.major else True)
# 
# 
#     # if the major is equal, but the minor is greater, then the version is always greater
#     assert Semver(0, 1, 0) > Semver(0, 0, 1)
#     assert Semver(0, 1, 0) > Semver(0, 0, 0)
#     assert Semver(0, 1, 1) > Semver(0, 0, 1)
#     assert Semver(0, 1, 1) > Semver(0, 0, 0)
#     assert for_all_pairs(lambda v1, v2: v1 > v2 if (v1.major == v2.major) and (v1.minor > v2.minor) else True)
# 
#     # if the major is equal, but the minor is smaller, then the version is always smaller
#     assert Semver(0, 0, 1) < Semver(0, 1, 0)
#     assert Semver(0, 0, 0) < Semver(0, 1, 0)
#     assert Semver(0, 0, 1) < Semver(0, 1, 1)
#     assert Semver(0, 0, 0) < Semver(0, 1, 1)
#     assert for_all_pairs(lambda v1, v2: v1 < v2 if (v1.major == v2.major) and (v1.minor < v2.minor) else True)
# 
# 
#     # if the major and minor are equal, but the patch is greater, then the version should be always greater
#     assert Semver(0, 0, 1) > Semver(0, 0, 0)
#     assert for_all_pairs(lambda v1, v2: v1 > v2 if (v1.major == v2.major) and (v1.minor == v2.minor) and (v1.minor > v2.minor) else True)
# 
#     # if the major and minor are equal, but the patch is smaller, then the version should be always smaller
#     assert Semver(0, 0, 0) < Semver(0, 0, 1)
#     assert for_all_pairs(lambda v1, v2: v1 < v2 if (v1.major == v2.major) and (v1.minor == v2.minor) and (v1.minor < v2.minor) else True)
# 
# 
# 
# 
# def test_parse_version(version_samples: list[Semver]):
# 
#     assert parse_version("0.0.0") == Semver(0, 0, 0)
#     assert parse_version("1.1.1") == Semver(1, 1, 1)
#     assert parse_version("9.8.7") == Semver(9, 8, 7)
#     assert parse_version("10.10.10") == Semver(10, 10, 10)
#     assert parse_version("1.1") == Semver(1, 1, 0)
#     assert parse_version("1") == Semver(1, 0, 0)
# 
#     # empty string
#     assert parse_version("") is None
# 
#     # untrimmed string
#     assert parse_version(" 0.0.0") is None
#     assert parse_version("0.0.0 ") is None
#     assert parse_version("0.0.0\n") is None
# 
#     # leading zero
#     assert parse_version("01.0.0") is None
# 
#     # trailing separator
#     assert parse_version("0.0.") is None
# 
#     # extra numbers
#     assert parse_version("1.1.1.1") is None
# 
#     
#     # the string representation of a version should always be parsed to the same version
#     assert all(version == parse_version(version.to_string()) for version in version_samples)
# 