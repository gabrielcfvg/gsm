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
from gsm.project_files import load_config_file
from gsm.project_files.version import SemverVersion, TagVersion, BranchVersion, CommitVersion
from gsm.version import Semver


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


# ---------------------------------------------------------------------------- #
#                                     tests                                    #
# ---------------------------------------------------------------------------- #


def test_config_file_loading(tmp_path: Path):

    # TODO: invalid semver string should panic

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
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()
    
    # missing remote should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""version = "1.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()
                
    # missing version should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()


    # ---------------------------- invalid field value --------------------------- #
                
    # path with a number instead of a string should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = 123           """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # version with a list instead of a string should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = [1, 0, 0]     """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # invalid semver string should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "foobar"      """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # ------------------------------- unknown field ------------------------------- #
                
    # unknown project field should panic
    config_file = "\n".join([
        r"""unknown = "unknown"     """,
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # unknown dependency field should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
        r"""unknown = "unknown"     """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # -------------------------------- null field -------------------------------- #
    
    # null path should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = ""            """,
        r"""remote  = "remote_foo"  """,
        r"""version = "1.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()
    
    # null remote should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = ""            """,
        r"""version = "1.0.0"       """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # null version should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""version = ""            """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()
    
    # null tag should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""tag     = ""            """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()

    # null branch should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""branch  = ""            """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()
    
    # null commit when using branch should panic
    config_file = "\n".join([
        r"""[[dependency]]          """,
        r"""path    = "deps/foo"    """,
        r"""remote  = "remote_foo"  """,
        r"""branch  = "foobar"      """,
        r"""commit  = ""            """,
    ])
    with create_tmp_fs_node(create_project_template(config_file)) as project_path:
        with tmp_change_dir(project_path):
            with pytest.raises(PanicException):
                config = load_config_file()
    




def test_lock_file_loading(tmp_path: Path):

    # TODO: branch without commit should panic
    # TODO: lock file without gsm version should panic
    # TODO: invalid hash string size should panic
    # TODO: invalid hash string chars should panic

    # -------------------------------- lock count -------------------------------- #

    # -------------------------- different version types ------------------------- #
    
    # ------------------------------- missing field ------------------------------ #
    
    # ---------------------------- invalid field value --------------------------- #

    # ------------------------------- unknown field ------------------------------- #
    pass

def test_mirrors_file_loading(tmp_path: Path):

    # -------------------------------- lock count -------------------------------- #

    # -------------------------- different version types ------------------------- #
    
    # ------------------------------- missing field ------------------------------ #
    
    # ---------------------------- invalid field value --------------------------- #

    # ------------------------------- unknown field ------------------------------- #
    pass