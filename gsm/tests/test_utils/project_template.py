# ---------------------------------- builtin --------------------------------- #
from typing import Optional
from pathlib import Path

# ----------------------------------- local ---------------------------------- #
from gsm.tests.test_utils.fs_template import FsT_Node, FsT_TextFile, FsT_Dir, create_tmp_fs_node



def create_project_template(
        config_file_str: str, lock_file_str: Optional[str] = None,
        mirrors_file_str: Optional[str] = None, name: str = "project") -> FsT_Node:
    
    project = FsT_Dir(name)
    project.add_child(FsT_TextFile("gsm.toml", config_file_str))

    if lock_file_str is not None:
        project.add_child(FsT_TextFile("gsm.lock", lock_file_str))

    if mirrors_file_str is not None:
        project.add_child(FsT_Dir(".gsm").add_child(FsT_Dir("mirrors").add_child(FsT_TextFile("mirrors.toml", mirrors_file_str))))

    return project


# ---------------------------------------------------------------------------- #
#                                     tests                                    #
# ---------------------------------------------------------------------------- #

def test_create_project_template(tmp_path: Path):

    # empty files
    config_file_str = ""
    lock_file_str = ""
    mirrors_file_str = ""
    with create_tmp_fs_node(create_project_template(config_file_str, lock_file_str, mirrors_file_str)) as project_path:
        assert project_path.exists()
        assert (project_path / "gsm.toml").exists()
        assert (project_path / "gsm.lock").exists()
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").exists()

    # non-empty files
    config_file_str = "config_str"
    lock_file_str = "lock_str"
    mirrors_file_str = "mirrors_str"
    with create_tmp_fs_node(create_project_template(config_file_str, lock_file_str, mirrors_file_str)) as project_path:
        assert project_path.exists()
        assert (project_path / "gsm.toml").exists()
        assert (project_path / "gsm.lock").exists()
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").exists()
        # check file contents
        assert (project_path / "gsm.toml").read_text() == config_file_str
        assert (project_path / "gsm.lock").read_text() == lock_file_str
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").read_text() == mirrors_file_str

    # config file only
    config_file_str = "config_str"
    with create_tmp_fs_node(create_project_template(config_file_str, None, None)) as project_path:
        assert project_path.exists()
        assert (project_path / "gsm.toml").exists()
        assert (project_path / "gsm.lock").exists() == False
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").exists() == False
        # check file contents
        assert (project_path / "gsm.toml").read_text() == config_file_str

    # no lock file
    config_file_str = "config_str"
    mirrors_file_str = "mirrors_str"
    with create_tmp_fs_node(create_project_template(config_file_str, None, mirrors_file_str)) as project_path:
        assert project_path.exists()
        assert (project_path / "gsm.toml").exists()
        assert (project_path / "gsm.lock").exists() == False
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").exists()
        # check file contents
        assert (project_path / "gsm.toml").read_text() == config_file_str
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").read_text() == mirrors_file_str

    # no mirrors file
    config_file_str = "config_str"
    lock_file_str = "lock_str"
    with create_tmp_fs_node(create_project_template(config_file_str, lock_file_str, None)) as project_path:
        assert project_path.exists()
        assert (project_path / "gsm.toml").exists()
        assert (project_path / "gsm.lock").exists()
        assert (project_path / ".gsm" / "mirrors" / "mirrors.toml").exists() == False
        # check file contents
        assert (project_path / "gsm.toml").read_text() == config_file_str
        assert (project_path / "gsm.lock").read_text() == lock_file_str
