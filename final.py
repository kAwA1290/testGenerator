import ast
from z3 import *


# ASTの以下の部分を探索する。
# ast.If
#     ast.left
#     ast.ops
#     ast.If.comparators
#         ast.Compare
#         ast.BoolOp
#         ast.Constant
#         ast.Name
#     ast.Constant

class SymbolicExecutor:

    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)

    def explore_path_constraints(self):
        for node in ast.walk(self.tree)
