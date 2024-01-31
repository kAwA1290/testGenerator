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
        res = f'({p.lefts[0]} {p.ops[0]} {p.rights[0]})'
        for bin_op in p.bin_ops:
            res = f'{"And" if bin_op == "&" else "Or"}(' + res
        for i in range(1, len(p.lefts)):
            res += f', ({p.lefts[i]} {p.ops[i]} {p.rights[i]}))'
        return res

    def to_logic(self, left, ops, comparators):
        self.to_parts(left, ops, comparators)
        pylogic = self.to_pylogic()
        z3logic = self.to_z3logic()
        return [pylogic, z3logic]

    def assign_to_logic(self, l):
        if isinstance(l, int):
            return f'{l}'
        elif isinstance(l[0], int):
            return f'{l[0]}{self.conv_op(l[1])}{l[2]}'
        return self.assign_to_logic(l[0]) + f'{self.conv_op(l[1])}{l[2]}'

    class Parts:

        def __init__(self):
            self.lefts = []
            self.ops = []
            self.rights = []
            self.bin_ops = []

class TestGenerator:

        def __init__(self):
            pass

        def generate(self, symbols, constraints, case_max):
            for s in symbols:
                exec("%s = Int('%s')" % (s, s))
            for equation in constraints:
                s = Solver()
                s.add(eval(equation[1]))
                cnt = 0
                if s.check() == unsat:
                    print(f'unsat: {equation[0]}')
                    continue
                print(f'sat: {equation[0]}')
                while(s.check() == sat and cnt < case_max):
                    m = s.model()
                    print(f'testcase: {m}')
                    cnt += 1
                print()

# ast.NodeVisitorは、astを探索するための基底クラスである。
# このクラスを継承し、探索したい型のメソッドをオーバーライドする。
class SymbolicVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self.clear()

    def clear(self):
        # 変数を格納する辞書, 変数に対する演算も保持する
        self.store = {}
        # 制約を格納するリスト, 各論理式を、[right, Operator, left]
        self.constraints = []
        self.symbols = set()
        self.testcases = []
        self.conv = Converter()
        self.generator = TestGenerator()
        self.if_depth = 0
        self.if_test_depth = 0

    def gen_testcases(self):
        self.generator.generate(self.symbols, self.constraints, 1)

    def visit_Assign(self, node: ast.Assign):
        target = node.targets[0].id
        value = self.visit(node.value)
        self.store[target] = self.conv.assign_to_logic(value)


    def visit_If(self, node: ast.If):
        self.if_depth += 1
        self_res = self.visit(node.test)
        self.if_depth -= 1
        body_res = []
        for body in node.body:
            if isinstance(body, ast.If):
                self.if_depth += 1
                body_res.append(self.visit(body))
                self.if_depth -= 1
        res = []
        for r in body_res:
            for rr in r:
                logic = [f'({self_res[0]}) & ({rr[0]})', f'And({self_res[1]}, {rr[1]})']
                res.append(logic)
        res.append(self_res)
        if self.if_depth == 0:
            for r in res:
                self.constraints.append(r)
        else:
            return res

    def visit_BoolOp(self, node: ast.BoolOp):
        op = node.op.__class__.__name__
        left = self.visit(node.values[0])
        right = self.visit(node.values[1])
        py = f'{left[0]} {self.conv.conv_op(op)} {right[0]}'
        z3 = f'{op}({left[1]}, {right[1]})'
        return [py, z3]

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        ops = [op.__class__.__name__ for op in node.ops]
        comparators = [self.visit(comparator) for comparator in node.comparators]
        self.conv.to_parts(left, ops, comparators)
        # return [pylogic, z3logic]
        res = self.conv.to_logic(left, ops, comparators)
        return res

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        op = node.op.__class__.__name__
        right = self.visit(node.right)
        return [left, op, right]

    def visit_Constant(self, node: ast.Constant):
        return node.value

    def visit_Name(self, node: ast.Name):
        self.symbols.add(node.id)
        try:
            res = self.store[node.id]
        except:
            res = node.id
        return res


if __name__ == "__main__":
    sample = """
if a > 0:
    if b < 2 & c > 3:
        print("a is not 1")
        if d == 2:
            if e == 2:
                pass
        if e == 2:
            pass
        if f == 2:
            pass
"""
    visitor = SymbolicVisitor()
    tree = ast.parse(sample)
    visitor.visit(tree)
    visitor.gen_testcases()

