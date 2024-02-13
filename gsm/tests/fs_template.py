# ---------------------------------- builtin --------------------------------- #
from typing import Generator
import shutil, os
from contextlib import contextmanager
from pathlib import Path

# -------------------------------- third party ------------------------------- #
import pytest

# ----------------------------------- local ---------------------------------- #
from gsm.log import PanicException, panic
from gsm.fs_template import FsT_Node, FsT_TextFile, FsT_Dir, build_fs_template



# ---------------------------------------------------------------------------- #
#                                  test utils                                  #
# ---------------------------------------------------------------------------- #

@contextmanager
def create_tmp_fs_node(node: FsT_Node, path: Path = Path(".")) -> Generator[Path, None, None]:
    
    assert path.is_dir()
    
    build_fs_template(node, path)
    dest_path = path / node.name

    try:
        yield dest_path
    finally:
        if dest_path.is_file():
            os.remove(dest_path)
        elif dest_path.is_dir():
            shutil.rmtree(dest_path)
        else:
            panic(f"internal error, unknow file type, path: {dest_path}")


@contextmanager
def create_tmp_dir(name: str, path: Path = Path(".")) -> Generator[Path, None, None]:

    assert path.is_dir()
    assert len(name) > 0

    dir_path = path / name
    assert dir_path.exists() == False
    os.mkdir(dir_path)

    try:
        yield dir_path
    finally:
        assert dir_path.is_dir()
        shutil.rmtree(dir_path)

# ---------------------------------------------------------------------------- #
#                                     tests                                    #
# ---------------------------------------------------------------------------- #

def test_template_node():

    # trying to create a node with a empty name should panics
    with pytest.raises(PanicException):
        FsT_TextFile("", "")

def test_template_dir():
    
    # trying to add two nodes with the same name in a directory should trigger a panic
    with pytest.raises(PanicException):
        FsT_Dir("dir").add_child(FsT_Dir("foo")).add_child(FsT_Dir("foo"))


def test_template_builder(tmp_path: Path):

    # if the destination dir already has an item with the same
    # name as the template root node name, the builder should panic
    with create_tmp_dir("dir", tmp_path) as _:
        with pytest.raises(PanicException):
            build_fs_template(FsT_Dir("dir"), tmp_path)

    # check if the template file is created correctly
    with create_tmp_dir("dir", tmp_path) as path:
        for file_content in ["", "abcd", "abc\ndef"]:
            template = FsT_TextFile("file", file_content)
            with create_tmp_fs_node(template, path) as file_path:
                assert file_path.is_file()
                assert open(file_path, "r").read() == file_content

    # check if the template dir is create correctly
    with create_tmp_fs_node(FsT_Dir("dir"), tmp_path) as dir_path:
        assert dir_path.is_dir()

    # check if a template dir subnodes are created correctly
    with create_tmp_fs_node(FsT_Dir("dir").add_child(FsT_TextFile("file", "")), tmp_path) as dir_path:
        assert (dir_path / "file").exists()

    # check if a template dir with multiple subnodes is created correctly
    template = FsT_Dir("dir")
    template.add_child(FsT_TextFile("file1", ""))
    template.add_child(FsT_TextFile("file2", ""))
    template.add_child(FsT_Dir("subdir"))
    with create_tmp_fs_node(template, tmp_path) as dir_path:
        for node_name in ["file1", "file2", "subdir"]:
            assert (dir_path / node_name).exists()

    # check if a template with more than 1 level of depth is created correctly
    template = FsT_Dir("dir1")
    template.add_child(FsT_Dir("dir2").add_child(FsT_TextFile("file", "")))
    with create_tmp_fs_node(template, tmp_path) as dir_path:
        assert (dir_path / "dir2").exists()
        assert (dir_path / "dir2" / "file").exists()
