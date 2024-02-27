# ---------------------------------- builtin --------------------------------- #
from pathlib import Path
from contextlib import contextmanager
import os

# -------------------------------- third party ------------------------------- #
import pytest

# ----------------------------------- local ---------------------------------- #
from gsm.log import PanicException
from gsm.tests.test_utils.project_template import create_project_template
from gsm.tests.test_utils.fs_template import create_tmp_fs_node
from gsm.project_files import load_config_file, load_lock_file
from gsm.project_files.version import SemverVersion, TagVersion, BranchVersion, CommitVersion
from gsm.semver import Semver
from gsm.version import GSM_VERSION


# ---------------------------------------------------------------------------- #
#                                  test utils                                  #
# ---------------------------------------------------------------------------- #

@contextmanager
def tmp_change_dir(dir: Path):
    
    assert dir.is_dir()
    old_dir = os.getcwd()
    
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(old_dir)

def hash_example() -> str:
    return "a" * 64


# ---------------------------------------------------------------------------- #
#                                     tests                                    #
# ---------------------------------------------------------------------------- #


def test_config_file_loading(tmp_path: Path):

    def shall_panic(config_file_str: str):
        with create_tmp_fs_node(create_project_template(config_file_str)) as project_path:
            with tmp_change_dir(project_path):
                with pytest.raises(PanicException):
                    _ = load_config_file()


    # ----------------------------- dependency count ----------------------------- #

    # empty config file
    config_file_str = ""
    with create_tmp_fs_node(create_project_template(config_file_str)) as project_path:
        with tmp_change_dir(project_path):
            config = load_config_file()
            assert len(config.dependencies) == 0

    # config file with one dependency
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            config = load_config_file()
            assert len(config.dependencies) == 1
            assert config.dependencies[0].path == Path("deps/foo")
            assert config.dependencies[0].remote == "remote_foo"
            assert config.dependencies[0].version == SemverVersion(Semver([1, 0, 0]))

    # config file with more than one dependencies
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
        r"""                        """,
        r"""[[dependency]]          """,
        r"""path    = "deps/bar"    """,
        r"""remote  = "remote_bar"  """,
        r"""version = "2.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            config = load_config_file()
            assert len(config.dependencies) == 2
            
            # dep 'foo'
            assert config.dependencies[0].path == Path("deps/foo")
            assert config.dependencies[0].remote == "remote_foo"
            assert config.dependencies[0].version == SemverVersion(Semver([1, 0, 0]))
            
            # dep 'bar'
            assert config.dependencies[1].path == Path("deps/bar")
            assert config.dependencies[1].remote == "remote_bar"
            assert config.dependencies[1].version == SemverVersion(Semver([2, 0, 0]))


    # -------------------------- different version types ------------------------- #
                
    # semver already tested at former assertions

    # tag version
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""tag     = "tag_foo"     """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            config = load_config_file()
            assert len(config.dependencies) == 1
            assert config.dependencies[0].path == Path("deps/foo")
            assert config.dependencies[0].remote == "remote_foo"
            assert config.dependencies[0].version == TagVersion("tag_foo")

    # branch version
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""branch  = "branch_foo"  """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            config = load_config_file()
            assert len(config.dependencies) == 1
            assert config.dependencies[0].path == Path("deps/foo")
            assert config.dependencies[0].remote == "remote_foo"
            assert config.dependencies[0].version == BranchVersion("branch_foo")

    # commit version
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""commit  = "commit_hash" """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            config = load_config_file()
            assert len(config.dependencies) == 1
            assert config.dependencies[0].path == Path("deps/foo")
            assert config.dependencies[0].remote == "remote_foo"
            assert config.dependencies[0].version == CommitVersion("commit_hash")

    # ------------------------------- missing field ------------------------------ #

    # missing path should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    shall_panic(config_file)

    # missing remote should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""version = "1.0.0"       """,
    ])
    shall_panic(config_file)

    # missing version should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
    ])
    shall_panic(config_file)


    # ---------------------------- invalid field value --------------------------- #
                
    # path with a number instead of a string should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = 123           """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    shall_panic(config_file)

    # version with a list instead of a string should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = [1, 0, 0]     """,
    ])
    shall_panic(config_file)

    # invalid semver string should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "foobar"      """,
    ])
    shall_panic(config_file)

    # ------------------------------- unknown field ------------------------------- #
                
    # unknown project field should panic
    config_file = "\n".join([
        r"""unknown = "unknown"     """,
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    shall_panic(config_file)

    # unknown dependency field should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
        r"""unknown = "unknown"     """,
    ])
    shall_panic(config_file)

    # -------------------------------- null field -------------------------------- #
    
    # TODO: we may need to check if the path is different from the project root
    # # null path should panic
    # config_file = "\n".join([
    #     r"""[[dependency]]          """,
    #     r"""path    = ""            """,
    #     r"""remote  = "remote_foo"  """,
    #     r"""version = "1.0.0"       """,
    # ])
    # with create_tmp_fs_node(create_project_template(config_file)) as project_path:
    #     with tmp_change_dir(project_path):
    #         with pytest.raises(PanicException):
    #             config = load_config_file()
    
    # null remote should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = ""            """,
        r"""version = "1.0.0"       """,
    ])
    shall_panic(config_file)

    # null version should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = ""            """,
    ])
    shall_panic(config_file)
    
    # null tag should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""tag     = ""            """,
    ])
    shall_panic(config_file)

    # null branch should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""branch  = ""            """,
    ])
    shall_panic(config_file)
    
    # null commit when using branch should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""branch  = "foobar"      """,
        r"""commit  = ""            """,
    ])
    shall_panic(config_file)
    

def test_lock_file_loading(tmp_path: Path):

    def shall_panic(lock_file_str: str):
        with create_tmp_fs_node(create_project_template(config_file_str="", lock_file_str=lock_file_str)) as project_path:
            with tmp_change_dir(project_path):
                with pytest.raises(PanicException):
                    _ = load_lock_file()

    def shall_not_panic(lock_file_str: str):
        with create_tmp_fs_node(create_project_template(config_file_str="", lock_file_str=lock_file_str)) as project_path:
            with tmp_change_dir(project_path):
                lock = load_lock_file()
                assert lock != None


    # -------------------------------- lock count -------------------------------- #
    # test if the parser can handle different amounts of locks in the lock file

    # no locks
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
    ])
    shall_not_panic(lock_file)

    # one lock
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        r"""path = "deps/foo"             """,
        f"""hash = "{hash_example()}"     """,
        r"""version = "0.1.0              """,
    ])
    shall_not_panic(lock_file)

    # more than one lock
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        r"""path = "deps/foo"             """,
        f"""hash = "{hash_example()}"     """,
        r"""version = "0.1.0              """,
        r"""                              """,
        r"""[[lock]]                      """,
        r"""path = "deps/bar"             """,
        f"""hash = "{hash_example()}"     """,
        r"""version = "0.1.0              """,
    ])
    shall_not_panic(lock_file)


    # ------------------------------ fields content ------------------------------ #
    # test if the parser parse the field values correctly

    # semver version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        r"""path = "deps/foo"             """,
        f"""hash = "{hash_example()}"     """,
        r"""version = "0.1.0              """,
    ])
    with create_tmp_fs_node(create_project_template(lock_file)) as project_path:
        with tmp_change_dir(project_path):
            lock = load_lock_file()
            assert lock != None
            assert len(lock.locks) == 1
            assert lock.locks[0].path == Path("deps/foo")
            assert lock.locks[0].hash == hash_example()
            assert lock.locks[0].version == SemverVersion(Semver([0, 1, 0]))

    # tag version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        r"""path = "deps/foo"             """,
        f"""hash = "{hash_example()}"     """,
        r"""tag  = "tag_foo               """,
    ])
    with create_tmp_fs_node(create_project_template(lock_file)) as project_path:
        with tmp_change_dir(project_path):
            lock = load_lock_file()
            assert lock != None
            assert len(lock.locks) == 1
            assert lock.locks[0].path == Path("deps/foo")
            assert lock.locks[0].hash == hash_example()
            assert lock.locks[0].version == TagVersion("tag_foo")

    # branch version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        r"""path   = "deps/foo"           """,
        f"""hash   = "{hash_example()}"   """,
        r"""branch = "branch_foo"         """,
        r"""commit = "commit_foo"         """,
    ])
    with create_tmp_fs_node(create_project_template(lock_file)) as project_path:
        with tmp_change_dir(project_path):
            lock = load_lock_file()
            assert lock != None
            assert len(lock.locks) == 1
            assert lock.locks[0].path == Path("deps/foo")
            assert lock.locks[0].hash == hash_example()
            assert lock.locks[0].version == BranchVersion("branch_foo", "commit_foo")

    # commit version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        r"""path = "deps/foo"             """,
        f"""hash = "{hash_example()}"     """,
        r"""commit = "commit_foo"         """,
    ])
    with create_tmp_fs_node(create_project_template(lock_file)) as project_path:
        with tmp_change_dir(project_path):
            lock = load_lock_file()
            assert lock != None
            assert len(lock.locks) == 1
            assert lock.locks[0].path == Path("deps/foo")
            assert lock.locks[0].hash == hash_example()
            assert lock.locks[0].version == CommitVersion("commit_foo")


    # ------------------------------- missing field ------------------------------ #
    # test if the parser panic if some of the requires fields are missing
    
    # missing gsm version should panic
    lock_file = "\n".join([
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # lock with missing path should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}" """,
        r"""[[lock]]                      """,
        f"""hash = "{hash_example()}"     """,
        r"""version = "0.1.0              """,
    ])
    shall_panic(lock_file)

    # lock with missing hash should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # lock without any version types should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
    ])
    shall_panic(lock_file)

    # lock with more than one version type should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
        r"""tag = "tag_foo"           """,
    ])
    shall_panic(lock_file)
    

    # ---------------------------- invalid field value --------------------------- #
    # test if the parser panic if some of the fields have invalid values

    # lock with non-string path
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = 123                """, # number instead of string
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = [1, 2, 3]          """, # array instead of string
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
    ])

    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = {foo = "bar"}      """, # dict instead of string
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
    ])

    # lock with non-string hash
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = 123                """, # number instead of string
        r"""version = "0.1.0          """,
    ])

    # lock with non-string tag version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""tag  = 123                """, # number instead of string
    ])
    shall_panic(lock_file)

    # lock with non-string branch version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"       """,
        r"""[[lock]]                    """,
        r"""path   = "deps/foo"         """,
        f"""hash   = "{hash_example()}" """,
        r"""branch = 123                """, # number instead of string
        r"""commit = "commit_foo"       """,
    ])
    shall_panic(lock_file)

    # lock with branch version and non-string commit version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"       """,
        r"""[[lock]]                    """,
        r"""path   = "deps/foo"         """,
        f"""hash   = "{hash_example()}" """,
        r"""branch = "branch_foo"       """,
        r"""commit = 123                """, # number instead of string
    ])
    shall_panic(lock_file)

    # lock with non-string commit version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""commit = 123              """, # number instead of string
    ])
    shall_panic(lock_file)

    # lock with non-string semver version
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""version = 123             """, # number instead of string
    ])
    shall_panic(lock_file)

    # lock with invalid semver string
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""version = "foobar"        """, # invalid semver string
    ])
    shall_panic(lock_file)

    # ------------------------------- empty string ------------------------------- #
    # test if the parser panic if some of the fields are empty strings

    # empty path should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = ""                 """,
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # empty hash should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = ""                 """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # empty tag version should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"    """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""tag  = ""                 """,
    ])
    shall_panic(lock_file)

    # empty branch version should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"       """,
        r"""[[lock]]                    """,
        r"""path   = "deps/foo"         """,
        f"""hash   = "{hash_example()}" """,
        r"""branch = ""                 """,
        r"""commit = "commit_foo"       """,
    ])
    shall_panic(lock_file)

    # empty commit version should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""commit = ""               """,
    ])

    # we do not need to test empty semver version because an empty string is not a valid semver string

    # ------------------------------- invalid hash ------------------------------- #
    # test if the parser will reject invalid hash strings

    # hash with less than 64 characters should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{"a" * 63}"       """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # hash with more than 64 characters should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{"a" * 65}"       """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # hash with non-hex characters should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{"g" + ("a" * 63)}""", # 'g' is not a valid hex character
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)


    # ------------------------------- unknown field ------------------------------- #
    # test if the parser panic if some of the fields are unknown

    # unknown project field should panic
    lock_file = "\n".join([
        r"""unknown = "unknown"       """,
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
    ])
    shall_panic(lock_file)

    # unknown lock field should panic
    lock_file = "\n".join([
        f"""gsm_version = "{GSM_VERSION}"     """,
        r"""[[lock]]                  """,
        r"""path = "deps/foo"         """,
        f"""hash = "{hash_example()}" """,
        r"""version = "0.1.0          """,
        r"""unknown = "unknown"       """,
    ])
    shall_panic(lock_file)


def test_mirrors_file_loading(tmp_path: Path):

    # -------------------------------- lock count -------------------------------- #

    # -------------------------- different version types ------------------------- #
    
    # ------------------------------- missing field ------------------------------ #
    
    # ---------------------------- invalid field value --------------------------- #

    # ------------------------------- unknown field ------------------------------- #
    pass