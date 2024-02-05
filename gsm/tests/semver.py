
# ---------------------------------- builtin --------------------------------- #
import random
from typing import Callable

# -------------------------------- third party ------------------------------- #
import pytest

# ----------------------------------- local ---------------------------------- #
from gsm.semver import *


SAMPLE_LIST_SIZE: int = 5 ** 3


def gen_version_list(amount: int) -> list[Semver]:

    cubic_root: int = int(round(amount ** (1./3.), 2))
    assert cubic_root ** 3 == amount
    output: list[Semver] = []

    for major in range(0, cubic_root):
        for minor in range(0, cubic_root):
            for patch in range(0, cubic_root):
                output.append(Semver(major, minor, patch))

    return output

@pytest.fixture(scope="module")
def version_samples() -> list[Semver]:

    return gen_version_list(SAMPLE_LIST_SIZE)

@pytest.fixture(scope="module")
def random_version_pair_samples() -> list[tuple[Semver, Semver]]:

    list1 = gen_version_list(SAMPLE_LIST_SIZE)
    list2 = gen_version_list(SAMPLE_LIST_SIZE)
    random.shuffle(list2)

    return [(list1[idx], list2[idx]) for idx in range(0, SAMPLE_LIST_SIZE)]


def test_semver_construction():

    with pytest.raises(RuntimeError):
        Semver(-1, 0, 0)

def test_semver_equality():

    assert Semver(0, 0, 0) == Semver(0, 0, 0)
    assert Semver(1, 2, 3) == Semver(1, 2, 3)

    assert Semver(7, 2, 3) != Semver(1, 2, 3)
    assert Semver(1, 8, 3) != Semver(1, 2, 3)
    assert Semver(1, 2, 9) != Semver(1, 2, 3)

    assert Semver(7, 8, 3) != Semver(1, 2, 3)
    assert Semver(1, 8, 9) != Semver(1, 2, 3)
    assert Semver(7, 2, 9) != Semver(1, 2, 3)

    assert Semver(7, 8, 9) != Semver(1, 2, 3)

def test_semver_compatibility(random_version_pair_samples: list[tuple[Semver, Semver]]):

    def for_all_pairs(func: Callable[[Semver, Semver], bool]) -> bool:
        return all(func(v1, v2) for v1, v2 in random_version_pair_samples)

    # version is always compatible with itself
    assert Semver(0, 0, 0).is_compatible_with(Semver(0, 0, 0))
    assert for_all_pairs(lambda v1, _: v1.is_compatible_with(v1))

    # version is always incompatible with another with a different major
    assert Semver(0, 0, 0).is_compatible_with(Semver(1, 0, 0)) == False
    assert Semver(1, 0, 0).is_compatible_with(Semver(0, 0, 0)) == False
    assert Semver(0, 0, 0).is_compatible_with(Semver(1, 1, 0)) == False
    assert Semver(0, 0, 0).is_compatible_with(Semver(1, 0, 1)) == False
    assert Semver(0, 0, 0).is_compatible_with(Semver(1, 1, 1)) == False
    assert for_all_pairs(lambda v1, v2: (v1.is_compatible_with(v2) == False) if (v1.major != v2.major) else True)

    # version is only compatible if minor is equal or greater than the other version minor
    # if the minor is equal, then patch should be equal or greater the other version patch
    assert Semver(0, 0, 0).is_compatible_with(Semver(0, 0, 0)) # equal
    assert Semver(0, 0, 0).is_compatible_with(Semver(0, 0, 1)) # patch greater
    assert Semver(0, 0, 0).is_compatible_with(Semver(0, 1, 0)) # minor greater
    assert Semver(0, 0, 0).is_compatible_with(Semver(0, 1, 1)) # both greater
    assert Semver(0, 1, 1).is_compatible_with(Semver(0, 1, 0)) == False # patch smaller
    assert Semver(0, 1, 1).is_compatible_with(Semver(0, 0, 1)) == False # minor smaller
    assert Semver(0, 1, 1).is_compatible_with(Semver(0, 0, 0)) == False # both smaller
    assert Semver(0, 1, 1).is_compatible_with(Semver(0, 0, 2)) == False # minor smaller && patch greater
    assert Semver(0, 1, 1).is_compatible_with(Semver(0, 2, 0)) # minor greater && patch smaller
    assert for_all_pairs(lambda v1, v2: v1.is_compatible_with(v2) if (v1.major == v2.major) and (v1.minor < v2.minor) else True)
    assert for_all_pairs(lambda v1, v2: v1.is_compatible_with(v2) if (v1.major == v2.major) and (v1.minor == v2.minor) and (v1.patch <= v2.patch) else True)

def test_semver_ordering(random_version_pair_samples: list[tuple[Semver, Semver]]):
    
    def for_all_pairs(func: Callable[[Semver, Semver], bool]) -> bool:
        return all(func(v1, v2) for v1, v2 in random_version_pair_samples)

    # any pair of version should be always and exclusively be: equal, greater, or smaller
    assert Semver(1, 0, 0) > Semver(0, 0, 0)
    assert not (Semver(1, 0, 0) < Semver(0, 0, 0))
    assert not (Semver(1, 0, 0) == Semver(0, 0, 0))
    assert Semver(0, 0, 0) < Semver(1, 0, 0)
    assert not (Semver(0, 0, 0) > Semver(1, 0, 0))
    assert not (Semver(0, 0, 0) == Semver(1, 0, 0))
    assert Semver(0, 0, 0) == Semver(0, 0, 0)
    assert not (Semver(0, 0, 0) > Semver(0, 0, 0))
    assert not (Semver(0, 0, 0) < Semver(0, 0, 0))
    assert for_all_pairs(lambda v1, v2: [(v1 == v2), (v1 > v2), (v1 < v2)].count(True) == 1)

    # if a version is different from another, they should be greater or smaller than the other one
    # the inverse shold be also true
    assert Semver(1, 2, 3) != Semver(3, 2, 1)
    assert not (Semver(1, 2, 3) > Semver(3, 2, 1))
    assert Semver(1, 2, 3) < Semver(3, 2, 1)
    assert for_all_pairs(lambda v1, v2: (v1 != v2) == ((v1 > v2) or (v1 < v2)))

    # if v1 is greater then v2, then v2 should be always smaller than v1
    assert (Semver(3, 2, 1) > Semver(1, 2, 3)) == (Semver(1, 2, 3) < Semver(3, 2, 1)) # maior
    assert (Semver(1, 2, 3) > Semver(3, 2, 1)) == (Semver(3, 2, 1) < Semver(1, 2, 3)) # menor
    assert (Semver(1, 2, 3) > Semver(1, 2, 3)) == (Semver(1, 2, 3) < Semver(1, 2, 3)) # igual
    assert for_all_pairs(lambda v1, v2: (v1 > v2) == (v2 < v1))

    # if v1 is equal-or-greater than v2, then v1 should never be smaller than v2
    assert (Semver(3, 2, 1) >= Semver(1, 2, 3)) == (not (Semver(3, 2, 1) < Semver(1, 2, 3))) # maior
    assert (Semver(1, 2, 3) >= Semver(3, 2, 1)) == (not (Semver(1, 2, 3) < Semver(3, 2, 1))) # menor
    assert (Semver(1, 2, 3) >= Semver(1, 2, 3)) == (not (Semver(1, 2, 3) < Semver(1, 2, 3))) # igual
    assert for_all_pairs(lambda v1, v2: (v1 >= v2) == (not (v1 < v2)))

    # if v1 is equal-or-smaller than v2, then v1 should never be greater than v2
    assert (Semver(3, 2, 1) <= Semver(1, 2, 3)) == (not (Semver(3, 2, 1) > Semver(1, 2, 3))) # maior
    assert (Semver(1, 2, 3) <= Semver(3, 2, 1)) == (not (Semver(1, 2, 3) > Semver(3, 2, 1))) # menor
    assert (Semver(1, 2, 3) <= Semver(1, 2, 3)) == (not (Semver(1, 2, 3) > Semver(1, 2, 3))) # igual
    assert for_all_pairs(lambda v1, v2: (v1 <= v2) == (not (v1 > v2)))

    # if v1 is equal-or-greater than v2, then v2 should be always equal-or-smaller than v1
    assert (Semver(3, 2, 1) >= Semver(1, 2, 3)) == (Semver(1, 2, 3) <= Semver(3, 2, 1)) # maior
    assert (Semver(1, 2, 3) >= Semver(3, 2, 1)) == (Semver(3, 2, 1) <= Semver(1, 2, 3)) # menor
    assert (Semver(1, 2, 3) >= Semver(1, 2, 3)) == (Semver(1, 2, 3) <= Semver(1, 2, 3)) # igual
    assert for_all_pairs(lambda v1, v2: (v1 >= v2) == (v2 <= v1))


    # if the version major is greater than the another version major, then it is always greater
    assert Semver(1, 0, 0) > Semver(0, 0, 0)
    assert Semver(1, 0, 0) > Semver(0, 1, 0)
    assert Semver(1, 0, 0) > Semver(0, 0, 1)
    assert Semver(1, 0, 0) > Semver(0, 1, 1)
    assert for_all_pairs(lambda v1, v2: v1 > v2 if v1.major > v2.major else True)

    # if the version major is smaller, then is is always smaller
    assert Semver(0, 0, 0) < Semver(1, 0, 0)
    assert Semver(0, 1, 0) < Semver(1, 0, 0)
    assert Semver(0, 0, 1) < Semver(1, 0, 0)
    assert Semver(0, 1, 1) < Semver(1, 0, 0)
    assert for_all_pairs(lambda v1, v2: v1 < v2 if v1.major < v2.major else True)


    # if the major is equal, but the minor is greater, then the version is always greater
    assert Semver(0, 1, 0) > Semver(0, 0, 1)
    assert Semver(0, 1, 0) > Semver(0, 0, 0)
    assert Semver(0, 1, 1) > Semver(0, 0, 1)
    assert Semver(0, 1, 1) > Semver(0, 0, 0)
    assert for_all_pairs(lambda v1, v2: v1 > v2 if (v1.major == v2.major) and (v1.minor > v2.minor) else True)

    # if the major is equal, but the minor is smaller, then the version is always smaller
    assert Semver(0, 0, 1) < Semver(0, 1, 0)
    assert Semver(0, 0, 0) < Semver(0, 1, 0)
    assert Semver(0, 0, 1) < Semver(0, 1, 1)
    assert Semver(0, 0, 0) < Semver(0, 1, 1)
    assert for_all_pairs(lambda v1, v2: v1 < v2 if (v1.major == v2.major) and (v1.minor < v2.minor) else True)


    # if the major and minor are equal, but the patch is greater, then the version should be always greater
    assert Semver(0, 0, 1) > Semver(0, 0, 0)
    assert for_all_pairs(lambda v1, v2: v1 > v2 if (v1.major == v2.major) and (v1.minor == v2.minor) and (v1.minor > v2.minor) else True)

    # if the major and minor are equal, but the patch is smaller, then the version should be always smaller
    assert Semver(0, 0, 0) < Semver(0, 0, 1)
    assert for_all_pairs(lambda v1, v2: v1 < v2 if (v1.major == v2.major) and (v1.minor == v2.minor) and (v1.minor < v2.minor) else True)




def test_parse_version(version_samples: list[Semver]):

    assert parse_version("0.0.0") == Semver(0, 0, 0)
    assert parse_version("1.1.1") == Semver(1, 1, 1)
    assert parse_version("9.8.7") == Semver(9, 8, 7)
    assert parse_version("10.10.10") == Semver(10, 10, 10)
    assert parse_version("1.1") == Semver(1, 1, 0)
    assert parse_version("1") == Semver(1, 0, 0)

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

    
    # the string representation of a version should always be parsed to the same version
    assert all(version == parse_version(version.to_string()) for version in version_samples)
