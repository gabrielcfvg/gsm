
# ---------------------------------- builtin --------------------------------- #
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import final, override, NoReturn
from pathlib import Path
from os import mkdir

# ----------------------------------- local ---------------------------------- #
from gsm.log import panic



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

            mkdir(path)
            self.path_stack.append(node.name)
            for child in node.children:
                child.visit(self)
            self.path_stack.pop()

    template_root.visit(Builder(dest_path))
