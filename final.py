import ast
from z3 import *

class Converter:

    def __init__(self):
        self.op_dict = {
            'Eq': "==",
            'NotEq': "!=",
            'Lt': "<",
            'LtE': "<=",
            'Gt': ">",
            'GtE': ">=",
            'And': "&",
            'Or': "|",
            'Add': "+",
            'Sub': "-",
            'Mult': "*",
            'Div': "/",
            'Mod': "%",
            'Pow': "**",
            'BitOr': "|",
            'BitAnd': "&",
        }
        self.parts = None

    def conv_op(self, op):
        try:
            return self.op_dict[op]
        except:
            raise Exception(f'Unknown operator: {op}')

    def to_parts(self, left, ops, comparators):
        parts = self.Parts()
        parts.lefts.append(left)
        parts.ops = [self.conv_op(op) for op in ops]
        for i, comparator in enumerate(comparators):
            if i == len(comparators) - 1:
                parts.rights.append(comparator)
                break
            parts.rights.append(comparator[0])
            parts.bin_ops.append(self.conv_op(comparator[1]))
            parts.lefts.append(comparator[2])
        self.parts = parts

    def to_pylogic(self):
        # TODO if True or a > 1:などの場合に対応する
        # TODO opsの長さが1の場合に対応する
        p = self.parts
        res = ''
        for i in range(len(p.lefts)):
            res += f'({p.lefts[i]} {p.ops[i]} {p.rights[i]})'
            if i < len(p.bin_ops):
                res += f' {p.bin_ops[i]} '
        return res

    def to_z3logic(self):
        p = self.parts
        variables = [f'({p.lefts[i]} {p.ops[i]} {p.rights[i]})' for i in range(len(p.lefts))]
        def build_z3logic(start, end):
            if start == end:
                return variables[symbols[start]]
            op = p.bin_ops[start]
            left_logic = variables[symbols[start]]
            right_logic = build_z3logic(start + 1, end)

            if op == '&':
                return And(left_logic, right_logic)
            elif op == '|':
                return Or(left_logic, right_logic)
            else:
                raise ValueError(f"Unsupported operator: {op}")
        z3_logic = build_z3logic(0, len(p.lefts) - 1)
        return z3_logic

    def to_logic(self, left, ops, comparators):
        self.to_parts(left, ops, comparators)
        pylogic = self.to_pylogic()
        z3logic = self.to_z3logic()
        return [pylogic, z3logic]

    class Parts:

        def __init__(self):
            self.lefts = []
            self.ops = []
            self.rights = []
            self.bin_ops = []

class TestGenerator:

        def __init__(self):
            self.solver = Solver()

        def generate(self, symbols, constraints):
            # 変数定義
            n = Int("n")
            x = Int("x")
            y = Int("y")
            
            # 基本制約
            s = Solver()
            s.add(n > 0, x > 0, y > 0)
            s.add(13*x > (n+110))
            s.add(7*y == (240-n))
            
            # 解を探索
            while(s.check() == sat):
                # 解の表示
                m = s.model()
                print(m)
                
                # 解を制約条件に追加
                s.add(Not(n == m[n]))

            #for constraint in constraints:
            #    self.solver.add(constraint)
            #print(self.solver.check())
            #print(self.solver.model())

# ast.NodeVisitorは、astを探索するための基底クラスである。
# このクラスを継承し、探索したい型のメソッドをオーバーライドする。
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
class SymbolicVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        # 変数を格納する辞書, 変数に対する演算も保持する
        self.store = {}
        # 制約を格納するリスト, 各論理式を、[right, Operator, left]
        self.constraints = []
        self.testcases = []
        self.conv = Converter()

    def visit_Assign(self, node: ast.Assign):
        # TODO 複数変数への代入に対応する
        #target = node.targets[0].id
        return ;

    def visit_If(self, node: ast.If):
        # Compare, BoolOpによって表される制約を抽出する
        print(node.test)
        print(self.visit(node.test))
        return ;

    def visit_BoolOp(self, node: ast.BoolOp):
        op = node.op.__class__.__name__
        left = self.visit(node.values[0])
        right = self.visit(node.values[1])
        return f'({left} {self.conv.conv_op(op)} {right})'

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        ops = [op.__class__.__name__ for op in node.ops]
        comparators = [self.visit(comparator) for comparator in node.comparators]
        self.conv.to_parts(left, ops, comparators)
        return self.conv.to_logic(left, ops, comparators)

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        op = node.op.__class__.__name__
        right = self.visit(node.right)
        return [left, op, right]

    def visit_Constant(self, node: ast.Constant):
        return node.value

    def visit_Name(self, node: ast.Name):
        return node.id


if __name__ == "__main__":
    sample = """
a = 1
b = 2 * b
c = 3 * a * b
d = 4 * a * b + c
e, f = 5, 6
if a == 1 & b == 2 & c > 3 & d < 4:
    print("a is 1")
"""
    visitor = SymbolicVisitor()
    tree = ast.parse(sample)
    visitor.generic_visit(tree)
    print()

    sample = """
a = 1
b = 2 * b
c = 3 * a * b
if a != 1 or b <= 2 & c > 3:
    print("a is 1")
"""
    visitor = SymbolicVisitor()
    tree = ast.parse(sample)
    visitor.generic_visit(tree)
    print()

    sample = """
a = 1
b = 2 * b
c = 3 * a * b
if True or a > 1 or False:
    print("a is 1")
"""
    visitor = SymbolicVisitor()
    tree = ast.parse(sample)
    visitor.generic_visit(tree)
    print()



