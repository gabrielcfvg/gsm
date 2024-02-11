
# disable private member warnings, since this is a test file
# pyright: reportPrivateUsage=none

# ---------------------------------- builtin --------------------------------- #
import random
from typing import Protocol, Callable
from functools import cache
from copy import copy

# -------------------------------- third party ------------------------------- #
import pytest

# ----------------------------------- local ---------------------------------- #
from gsm.semver import *



# ---------------------------------------------------------------------------- #
#                                     utils                                    #
# ---------------------------------------------------------------------------- #

MAX_VERSION_NUMBER = 5

REQ_NON_ZERO_MAJOR: Callable[[Semver, Semver], bool] = lambda v1, v2: (v1._major() != 0) and (v2._major() != 0)
REQ_EQUAL_MAJOR: Callable[[Semver, Semver], bool] = lambda v1, v2: REQ_NON_ZERO_MAJOR(v1, v2) and v1._major() == v2._major()
REQ_PRESENT_MINOR: Callable[[Semver, Semver], bool] = lambda v1, v2: v1._core_lenght() > 1 and v2._core_lenght() > 1
REQ_PRESENT_PATCH: Callable[[Semver, Semver], bool] = lambda v1, v2: REQ_PRESENT_MINOR(v1, v2) and v1._core_lenght() > 2 and v2._core_lenght() > 2


class ForAllPairsFunctor(Protocol):
    def __call__(
            self,
            func: Callable[[Semver, Semver], bool],
            filters: list[Callable[[Semver, Semver], bool]] = [],
            prereqs: list[Callable[[Semver, Semver], bool]] = []) -> bool: ...

def gen_for_all_pairs(pair_list: list[tuple[Semver, Semver]]) -> ForAllPairsFunctor:
    
    def for_all_pairs(
            func: Callable[[Semver, Semver], bool],
            filters: list[Callable[[Semver, Semver], bool]] = [],
            prereqs: list[Callable[[Semver, Semver], bool]] = []) -> bool:
        
        for v1, v2 in pair_list:
            
            if not all(filter(v1, v2) for filter in filters):
                continue

            if not all(req(v1, v2) for req in prereqs):
                if func(v1, v2):
                    return False
                else:
                    continue

            if not func(v1, v2):
                return False
            
        return True
        
    return for_all_pairs


class ForAllVersionsFunctor(Protocol):
    def __call__(
            self,
            func: Callable[[Semver], bool],
            filters: list[Callable[[Semver], bool]] = [],
            prereqs: list[Callable[[Semver], bool]] = []) -> bool: ...

def gen_for_all_versions(version_list: list[Semver]) -> ForAllVersionsFunctor:
    
    def for_all_versions(
            func: Callable[[Semver], bool],
            filters: list[Callable[[Semver], bool]] = [],
            prereqs: list[Callable[[Semver], bool]] = []) -> bool:
        
        for version in version_list:
            
            if not all(filter(version) for filter in filters):
                continue

            if not all(req(version) for req in prereqs):
                if func(version):
                    return False
                else:
                    continue

            if not func(version):
                return False
            
        return True
        
    return for_all_versions


def gen_core_arrangement_with_repetition(
        core_values: set[int], core_gen_null: bool = True,
        always_included: set[int] = set()) -> list[list[int]]:
    
    assert always_included.issubset(core_values)
    output: list[list[int]] = []

    def push(core_list: list[int]):

        for obligatory_item in always_included:
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


@cache
def calc_version_list_size() -> int:
    return (MAX_VERSION_NUMBER ** 3) + (MAX_VERSION_NUMBER ** 2) + MAX_VERSION_NUMBER


@cache
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
def version_pair_samples() -> list[tuple[Semver, Semver]]:

    list1 = gen_version_list()
    list2 = copy(list1)
    random.shuffle(list2)

    assert len(list1) == len(list2)
    return [(list1[idx], list2[idx]) for idx in range(0, len(list1))]


# ---------------------------------------------------------------------------- #
#                                     tests                                    #
# ---------------------------------------------------------------------------- #

def test_gen_core_arrangement():

    # fixed value test
    test_result = gen_core_arrangement_with_repetition({0, 1})
    test_expected_items = [
        [0], [1], [0, 0], [0, 1], [1, 0], [1, 1],
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
        [1, 1, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]
    ]
    assert len(test_result) == len(test_expected_items)
    assert all(item in test_result for item in test_expected_items)

    # test output length
    value_sets = [{i for i in range(0, j)} for j in range(1, 5)]
    for value_set in value_sets:
        assert len(gen_core_arrangement_with_repetition(value_set)) == len(value_set)**3 + len(value_set)**2 + len(value_set)
        assert len(gen_core_arrangement_with_repetition(value_set, core_gen_null=False)) == len(value_set)**3


def test_random_version_pair_samples(version_pair_samples: list[tuple[Semver, Semver]]):

    # the pair list should have the same size as the version list
    assert len(version_pair_samples) == calc_version_list_size()

    # the pair list should have no repeated pairs
    assert len(set(version_pair_samples)) == len(version_pair_samples)


def test_semver_construction():

    # inputing a core list with no values should raise an error
    with pytest.raises(RuntimeError):
        Semver(core=[])

    # inputing negative values to core list should raise an error
    for core_values in gen_core_arrangement_with_repetition({0, -1}, always_included={-1}):
        with pytest.raises(RuntimeError):
            Semver(core=core_values)


def test_semver_equality(version_pair_samples: list[tuple[Semver, Semver]]):

    for_all_pairs = gen_for_all_pairs(version_pair_samples)

    # version is always equal to itself
    assert Semver([0]) == Semver([0])
    assert Semver([0, 0]) == Semver([0, 0])
    assert Semver([0, 0, 0]) == Semver([0, 0, 0])
    assert for_all_pairs(lambda v1, v2: (v1 == v1) and (v2 == v2))

    # versions with different core lenght should always be different
    assert Semver([0]) != Semver([0, 0])
    assert Semver([0, 0]) != Semver([0, 0, 0])
    assert Semver([0]) != Semver([0, 0, 0])
    assert for_all_pairs(
        func=lambda v1, v2: v1 != v2,
        filters=[lambda v1, v2: v1._core_lenght() != v2._core_lenght()]
    )

    # versions with any different core should always be different
    assert Semver([0]) != Semver([1])
    assert Semver([0, 0]) != Semver([1, 0])
    assert Semver([0, 0, 0]) != Semver([1, 0, 0])
    assert for_all_pairs(
        func=lambda v1, v2: v1 != v2,
        filters=[lambda v1, v2: any(i1 != i2 for i1, i2 in zip(v1._core.items, v2._core.items))]
    )


def test_semver_compatibility(version_samples: list[Semver], version_pair_samples: list[tuple[Semver, Semver]]):

    for_all_versions = gen_for_all_versions(version_samples)
    for_all_pairs = gen_for_all_pairs(version_pair_samples)
    

    # version is always compatible with itself
    assert Semver([0]).is_compatible_with(Semver([0]))
    assert Semver([0, 0]).is_compatible_with(Semver([0, 0]))
    assert Semver([0, 0, 0]).is_compatible_with(Semver([0, 0, 0]))
    assert for_all_versions(lambda v: v.is_compatible_with(v))

    # version is always incompatible with another with a different major
    assert Semver([0]).is_compatible_with(Semver([1])) == False
    assert Semver([1]).is_compatible_with(Semver([0])) == False
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2) == False,
        filters=[lambda v1, v2: v1._major() != v2._major()]
    )

    # if the version major is 0, it only is compatible with another version, if
    # and only if, it is equal to the other version.
    # in other words, if the major is 0, then the version is only compatible
    # with itself.
    assert Semver([0, 0, 0]).is_compatible_with(Semver([0, 0, 0]))
    assert Semver([0, 0, 0]).is_compatible_with(Semver([0, 0, 1])) == False
    assert Semver([0, 0, 0]).is_compatible_with(Semver([0, 1, 0])) == False
    assert Semver([0, 0, 0]).is_compatible_with(Semver([0, 1, 1])) == False
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[lambda v1, v2: (v1._major() == 0) or (v2._major() == 0)], # any of the two majors being 0 is enough
        prereqs=[lambda v1, v2: v1 == v2]
    )

    # a null version number has less precedence than any other number
    # if a version minor is null, then it is compatible with any other greater
    # version with the same major
    assert Semver([1]).is_compatible_with(Semver([1])) # both null
    assert Semver([1]).is_compatible_with(Semver([1, 0])) # minor non-null
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_EQUAL_MAJOR,
            lambda v1, v2: v1._core_lenght() == 1 # if the size is 1, only major is present and the minor is null
        ]
    )

    # if a version patch is null, then it is compatible with any other greater
    # version with the same major
    assert Semver([1, 1]).is_compatible_with(Semver([1, 1])) # both with equal minor and null patch
    assert Semver([1, 1]).is_compatible_with(Semver([1, 1, 0])) # equal minor and non-null patch
    assert Semver([1, 1]).is_compatible_with(Semver([1, 2])) # greater minor and null patch
    assert Semver([1, 1]).is_compatible_with(Semver([1, 2, 0])) # greater minor and non-null patch
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_EQUAL_MAJOR,
            lambda v1, v2: v1._core_lenght() == 2, # if the size is 2, then major and minor are present and the patch is null
        ],
        prereqs=[lambda v1, v2: v2 >= v1]
    )


    # if v2 patch is null, v1 can only be compatible with v2 if v1 minor is
    # smaller or if v1 minor is equal and v1 patch is also null
    assert Semver([1, 1]).is_compatible_with(Semver([1, 1])) # equal minor and patch
    assert Semver([1, 0]).is_compatible_with(Semver([1, 1])) # minor smaller
    assert Semver([1, 0, 0]).is_compatible_with(Semver([1, 1])) # minor smaller
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            lambda v1, v2: v2._core_lenght() == 2, # if the size is 2, then major and minor are present and the patch is null
        ],
        prereqs=[
            lambda v1, v2: v1._minor() < v2._minor()
        ]
    )
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            lambda v1, v2: v2._core_lenght() == 2, # if the size is 2, then major and minor are present and the patch is null
            lambda v1, v2: v1._minor() == v2._minor() # if the minors are equal
        ],
        prereqs=[
            lambda v1, v2: v1._core_lenght() == 2
        ]
    )

    # if v2 minor is null, v1 can only be compatible with v2 if v1 minor is also null
    assert Semver([1]).is_compatible_with(Semver([1])) # both non-null minor
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_EQUAL_MAJOR,
            lambda v1, v2: v2._core_lenght() == 1, # if the size is 1, only major is present and the minor is null
        ],
        prereqs=[lambda v1, v2: v1._core_lenght() == 1] # v1 minor also null
    )

    # version is only compatible if minor is equal or greater than the other version minor
    # if the minor is equal, then patch should be equal or greater the other version patch
    assert Semver([1, 0, 0]).is_compatible_with(Semver([1, 0, 0])) # equal
    assert Semver([1, 0, 0]).is_compatible_with(Semver([1, 0, 1])) # patch greater
    assert Semver([1, 0, 0]).is_compatible_with(Semver([1, 1, 0])) # minor greater
    assert Semver([1, 0, 0]).is_compatible_with(Semver([1, 1, 1])) # both greater
    assert Semver([1, 1, 1]).is_compatible_with(Semver([1, 1, 0])) == False # patch smaller
    assert Semver([1, 1, 1]).is_compatible_with(Semver([1, 0, 1])) == False # minor smaller
    assert Semver([1, 1, 1]).is_compatible_with(Semver([1, 0, 0])) == False # both smaller
    assert Semver([1, 1, 1]).is_compatible_with(Semver([1, 0, 2])) == False # minor smaller && patch greater
    assert Semver([1, 1, 1]).is_compatible_with(Semver([1, 2, 0])) # minor greater && patch smaller
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_NON_ZERO_MAJOR,
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            lambda v1, v2: v1._minor() != v2._minor()
        ],
        prereqs=[lambda v1, v2: v1._minor() < v2._minor()]
    )
    assert for_all_pairs(
        lambda v1, v2: v1.is_compatible_with(v2),
        filters=[
            REQ_NON_ZERO_MAJOR,
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_PATCH,
            lambda v1, v2: v1._minor() == v2._minor(),
        ],
        prereqs=[
            lambda v1, v2: v1._patch() <= v2._patch()
        ]
    )


def test_semver_ordering(version_pair_samples: list[tuple[Semver, Semver]]):
    
    for_all_pairs = gen_for_all_pairs(version_pair_samples)


    # TODO: testar a não-equidade das versões com cores nulos
    # ex: 0.1 != 0.1.0, 0.1.0 > 0.1

    # any pair of version should be always and exclusively be: equal, greater, or smaller
    assert Semver([1, 0, 0]) > Semver([0, 0, 0])
    assert not (Semver([1, 0, 0]) < Semver([0, 0, 0]))
    assert not (Semver([1, 0, 0]) == Semver([0, 0, 0]))
    assert Semver([0, 0, 0]) < Semver([1, 0, 0])
    assert not (Semver([0, 0, 0]) > Semver([1, 0, 0]))
    assert not (Semver([0, 0, 0]) == Semver([1, 0, 0]))
    assert Semver([0, 0, 0]) == Semver([0, 0, 0])
    assert not (Semver([0, 0, 0]) > Semver([0, 0, 0]))
    assert not (Semver([0, 0, 0]) < Semver([0, 0, 0]))
    assert for_all_pairs(lambda v1, v2: [(v1 == v2), (v1 > v2), (v1 < v2)].count(True) == 1)

    # if a version is different from another, they should be greater or smaller than the other one
    # the inverse shold be also true
    assert Semver([1, 2, 3]) != Semver([3, 2, 1])
    assert not (Semver([1, 2, 3]) > Semver([3, 2, 1]))
    assert Semver([1, 2, 3]) < Semver([3, 2, 1])
    assert for_all_pairs(lambda v1, v2: (v1 != v2) == ((v1 > v2) or (v1 < v2)))

    # if v1 is greater then v2, then v2 should be always smaller than v1
    assert (Semver([3, 2, 1]) > Semver([1, 2, 3])) == (Semver([1, 2, 3]) < Semver([3, 2, 1])) # maior
    assert (Semver([1, 2, 3]) > Semver([3, 2, 1])) == (Semver([3, 2, 1]) < Semver([1, 2, 3])) # menor
    assert (Semver([1, 2, 3]) > Semver([1, 2, 3])) == (Semver([1, 2, 3]) < Semver([1, 2, 3])) # igual
    assert for_all_pairs(lambda v1, v2: (v1 > v2) == (v2 < v1))

    # if v1 is equal-or-greater than v2, then v1 should never be smaller than v2
    assert (Semver([3, 2, 1]) >= Semver([1, 2, 3])) == (not (Semver([3, 2, 1]) < Semver([1, 2, 3]))) # maior
    assert (Semver([1, 2, 3]) >= Semver([3, 2, 1])) == (not (Semver([1, 2, 3]) < Semver([3, 2, 1]))) # menor
    assert (Semver([1, 2, 3]) >= Semver([1, 2, 3])) == (not (Semver([1, 2, 3]) < Semver([1, 2, 3]))) # igual
    assert for_all_pairs(lambda v1, v2: (v1 >= v2) == (not (v1 < v2)))

    # if v1 is equal-or-smaller than v2, then v1 should never be greater than v2
    assert (Semver([3, 2, 1]) <= Semver([1, 2, 3])) == (not (Semver([3, 2, 1]) > Semver([1, 2, 3]))) # maior
    assert (Semver([1, 2, 3]) <= Semver([3, 2, 1])) == (not (Semver([1, 2, 3]) > Semver([3, 2, 1]))) # menor
    assert (Semver([1, 2, 3]) <= Semver([1, 2, 3])) == (not (Semver([1, 2, 3]) > Semver([1, 2, 3]))) # igual
    assert for_all_pairs(lambda v1, v2: (v1 <= v2) == (not (v1 > v2)))

    # if v1 is equal-or-greater than v2, then v2 should be always equal-or-smaller than v1
    assert (Semver([3, 2, 1]) >= Semver([1, 2, 3])) == (Semver([1, 2, 3]) <= Semver([3, 2, 1])) # maior
    assert (Semver([1, 2, 3]) >= Semver([3, 2, 1])) == (Semver([3, 2, 1]) <= Semver([1, 2, 3])) # menor
    assert (Semver([1, 2, 3]) >= Semver([1, 2, 3])) == (Semver([1, 2, 3]) <= Semver([1, 2, 3])) # igual
    assert for_all_pairs(lambda v1, v2: (v1 >= v2) == (v2 <= v1))


    # if the version major is greater than the another version major, then it is always greater
    assert Semver([1, 0, 0]) > Semver([0, 0, 0])
    assert Semver([1, 0, 0]) > Semver([0, 1, 0])
    assert Semver([1, 0, 0]) > Semver([0, 0, 1])
    assert Semver([1, 0, 0]) > Semver([0, 1, 1])
    assert for_all_pairs(
        lambda v1, v2: v1 > v2,
        filters=[lambda v1, v2: v1._major() > v2._major()]
    )

    # if the version major is smaller, then is is always smaller
    assert Semver([0, 0, 0]) < Semver([1, 0, 0])
    assert Semver([0, 1, 0]) < Semver([1, 0, 0])
    assert Semver([0, 0, 1]) < Semver([1, 0, 0])
    assert Semver([0, 1, 1]) < Semver([1, 0, 0])
    assert for_all_pairs(
        lambda v1, v2: v1 < v2,
        filters=[lambda v1, v2: v1._major() < v2._major()]
    )

    # if the major is equal, but the minor is greater, then the version is always greater
    assert Semver([0, 1, 0]) > Semver([0, 0, 1])
    assert Semver([0, 1, 0]) > Semver([0, 0, 0])
    assert Semver([0, 1, 1]) > Semver([0, 0, 1])
    assert Semver([0, 1, 1]) > Semver([0, 0, 0])
    assert for_all_pairs(
        lambda v1, v2: v1 > v2,
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            lambda v1, v2: v1._minor() > v2._minor()
        ],
    )

    # if the major is equal, but the minor is smaller, then the version is always smaller
    assert Semver([0, 0, 1]) < Semver([0, 1, 0])
    assert Semver([0, 0, 0]) < Semver([0, 1, 0])
    assert Semver([0, 0, 1]) < Semver([0, 1, 1])
    assert Semver([0, 0, 0]) < Semver([0, 1, 1])
    assert for_all_pairs(
        lambda v1, v2: v1 < v2,
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            lambda v1, v2: v1._minor() < v2._minor()
        ]
    )

    # if the major is equal, but one of the minors are null, then the one with
    # the non-null minor is always greater
    assert Semver([0, 1, 0]) > Semver([0, 1])
    assert Semver([0, 1]) < Semver([0, 1, 0])
    assert for_all_pairs(
        lambda v1, v2: v1 > v2,
        filters=[
            REQ_EQUAL_MAJOR,
            lambda v1, v2: v1._core_lenght() >= 2,
            lambda v1, v2: v2._core_lenght() == 1
        ]
    )


    # if the major and minor are equal, but the patch is greater, then the version should be always greater
    assert Semver([0, 0, 1]) > Semver([0, 0, 0])
    assert for_all_pairs(
        lambda v1, v2: v1 > v2,
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            REQ_PRESENT_PATCH,
            lambda v1, v2: v1._minor() == v2._minor(),
            lambda v1, v2: v1._patch() > v2._patch()
        ]
    )

    # if the major and minor are equal, but the patch is smaller, then the version should be always smaller
    assert Semver([0, 0, 0]) < Semver([0, 0, 1])
    assert for_all_pairs(
        lambda v1, v2: v1 < v2,
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            REQ_PRESENT_PATCH,
            lambda v1, v2: v1._minor() == v2._minor(),
            lambda v1, v2: v1._patch() < v2._patch()
        ]
    )

    # if the major and minor are equal, but one of the patches are null, then 
    # the one with the non-null patch is always greater
    assert Semver([0, 0, 0]) > Semver([0, 0])
    assert Semver([0, 0]) < Semver([0, 0, 0])
    assert for_all_pairs(
        lambda v1, v2: v1 > v2,
        filters=[
            REQ_EQUAL_MAJOR,
            REQ_PRESENT_MINOR,
            lambda v1, v2: v1._minor() == v2._minor(),
            lambda v1, v2: v1._core_lenght() > 2,
            lambda v1, v2: v2._core_lenght() == 2
        ]
    )


def test_parse_version(version_samples: list[Semver]):

    assert parse_version("0.0.0") == Semver([0, 0, 0])
    assert parse_version("1.1.1") == Semver([1, 1, 1])
    assert parse_version("9.8.7") == Semver([9, 8, 7])
    assert parse_version("10.10.10") == Semver([10, 10, 10])
    assert parse_version("1.1") == Semver([1, 1])
    assert parse_version("1") == Semver([1])

    # empty string
    assert parse_version("") is None

    # untrimmed string
    assert parse_version(" 0.0.0") is None
    assert parse_version("0.0.0 ") is None
    assert parse_version("0.0.0\n") is None

    # leading zero
    assert parse_version("01.0.0") is None

    # trailing separator
    assert parse_version("0.0.") is None

    # extra numbers
    assert parse_version("1.1.1.1") is None


    # version with pre-release or build metadata should throw an error
    unsuported_versions = [
        "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-0.3.7", "1.0.0-x.7.z.92", # pre-release
        "1.0.0+20130313144700", # build metadata
        "1.0.0-beta+exp.sha.5114f85", # pre-release and build metadata
    ]
    for version in unsuported_versions:
        with pytest.raises(VersionParseError):
            parse_version(version)

    
    # the string representation of a version should always be parsed to the same version
    assert all(version == parse_version(version.to_string()) for version in version_samples)
