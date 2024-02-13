
# ---------------------------------- builtin --------------------------------- #
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import final, override, NoReturn, Generator
from pathlib import Path
import os, shutil
from contextlib import contextmanager

# -------------------------------- third party ------------------------------- #
import pytest

# ----------------------------------- local ---------------------------------- #
from gsm.log import panic, PanicException



class FsT_NodeVisitor(ABC):

    @abstractmethod
    def visit_file(self, node: FsT_TextFile): ...

    @abstractmethod
    def visit_dir(self, node: FsT_Dir): ...


class FsT_Node(ABC):
    _name: str

    def __init__(self, name: str):
        
        if len(name) == 0:
            panic("internal_error: fs template node name must not be empty")

        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def visit(self, visitor: FsT_NodeVisitor): ...


class FsT_TextFile(FsT_Node):
    content: str

    def __init__(self, name: str, content: str):
        super().__init__(name)
        self.content = content

    @final
    @override
    def visit(self, visitor: FsT_NodeVisitor):
        visitor.visit_file(self)

class FsT_Dir(FsT_Node):
    _children: dict[str, FsT_Node]

    def __init__(self, name: str):
        super().__init__(name)
        self._children = {}

    def add_child(self, child: FsT_Node) -> FsT_Dir:
        
        if child.name in self._children:
            panic(f"child with name '{child.name}' already exists")
        
        self._children[child.name] = child

        return self
    
    @property
    def children(self) -> list[FsT_Node]:
        return [value for value in self._children.values()]

    @final
    @override
    def visit(self, visitor: FsT_NodeVisitor):
        visitor.visit_dir(self)



def build_fs_template(template_root: FsT_Node, dest_path: Path) -> None:

    @final
    class Builder(FsT_NodeVisitor):
        path_stack: list[str]

        def __init__(self, dest_path: Path):
            self.path_stack = [str(dest_path)]

        def get_path(self, node: FsT_Node) -> Path:
            return Path(*self.path_stack, node.name)
        
        def handle_repeated_node(self, node: FsT_Node) -> NoReturn:

            path = self.get_path(node)
            if len(self.path_stack) == 0:
                panic("error: the destination folder already contains a file or directory with the same name as the template root node"
                      f"path: {path.parent}, name: {node.name}")
            else:
                panic(f"internal error: a node with the same name already exists, path: {path.parent}, name: {node.name}")

        @override
        def visit_file(self, node: FsT_TextFile):
            
            path = self.get_path(node)
            if path.exists():
                self.handle_repeated_node(node)

            with open(path, "w") as file:
                file.write(node.content)

        @override
        def visit_dir(self, node: FsT_Dir):
            
            path = self.get_path(node)

            if path.exists():
                self.handle_repeated_node(node)

            os.mkdir(path)
            self.path_stack.append(node.name)
            for child in node.children:
                child.visit(self)
            self.path_stack.pop()

    template_root.visit(Builder(dest_path))


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
