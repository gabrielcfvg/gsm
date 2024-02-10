
# ---------------------------------- builtin --------------------------------- #
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import final, override, Any
from pathlib import Path

# ----------------------------------- local ---------------------------------- #
from log import panic


class FsT_NodeVisitor(ABC):

    @abstractmethod
    def visit_file(self, node: FsT_TextFile, return_value: Any): ...

    @abstractmethod
    def visit_dir(self, node: FsT_Dir, return_value: Any): ...


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
    def visit(self, visitor: FsT_NodeVisitor, return_value: Any): ...


class FsT_TextFile(FsT_Node):

    def __init__(self, name: str, content: str):
        super().__init__(name)

    @final
    @override
    def visit(self, visitor: FsT_NodeVisitor, return_value: Any):
        visitor.visit_file(self, return_value)

class FsT_Dir(FsT_Node):
    _children: dict[str, FsT_Node]

    def __init__(self, name: str):
        super().__init__(name)
        self._children = {}

    def add_child(self, child: FsT_Node):
        
        if child.name in self._children:
            panic(f"child with name '{child.name}' already exists")
        
        self._children[child.name] = child

    @final
    @override
    def visit(self, visitor: FsT_NodeVisitor, return_value: Any):
        visitor.visit_dir(self, return_value)



def build_fs_template(fst_node: FsT_Node, path: Path) -> None:

    class Builder(FsT_NodeVisitor):

        @override
        def visit_file(self, node: FsT_TextFile, return_value: Any):
            pass

        @override
        def visit_dir(self, node: FsT_Dir, return_value: Any):
            pass

    pass


#
# class Template: ...
# template = Template()
# whith create_from_template(template, tmp_dir) as fs:
#    fs operations...
#


