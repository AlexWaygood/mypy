import ast
import itertools
import pathlib

names = set[str]()

class ImportFinder(ast.NodeVisitor):
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.generic_visit(node)
        if node.module != "py":
            return
        names.update({obj.name for obj in node.names})

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.generic_visit(node)
        match node:
            case ast.Attribute(ast.Name("py"), attr):
                names.add(attr)
            case _:
                pass


for path in itertools.chain(
    pathlib.Path("mypy").rglob("*.py"),
    pathlib.Path("mypyc").rglob("*.py")
):
    ImportFinder().visit(ast.parse(path.read_text()))

print(names)
