import ast
from z3 import *

def ast_to_z3_expr(node, variables):
    if isinstance(node, ast.Name):
        var_id = str(node.id)
        if var_id.isdigit():
            return Real("var_" + var_id)
        return Real(var_id) if var_id in variables else None
    elif isinstance(node, ast.BinOp):
        left = ast_to_z3_expr(node.left, variables)
        right = ast_to_z3_expr(node.right, variables)
        op = node.op
        if left is not None and right is not None:
            if isinstance(op, ast.Add):
                return left + right
            elif isinstance(op, ast.Sub):
                return left - right
            elif isinstance(op, ast.Mult):
                return left * right
            elif isinstance(op, ast.Div):
                return left / right
            elif isinstance(op, ast.Mod):
                return left % right
    elif isinstance(node, ast.Compare):
        print(ast.dump(node))
        left = ast_to_z3_expr(node.left, variables)
        ops = node.ops
        comparators = [ast_to_z3_expr(comp, variables) for comp in node.comparators]
        constraints = []
        for op, right in zip(ops, comparators):
            if left is not None and right is not None:
                if isinstance(op, ast.Eq):
                    constraints.append(left == right)
                elif isinstance(op, ast.NotEq):
                    constraints.append(left != right)
                elif isinstance(op, ast.Lt):
                    constraints.append(left < right)
                elif isinstance(op, ast.LtE):
                    constraints.append(left <= right)
                elif isinstance(op, ast.Gt):
                    constraints.append(left > right)
                elif isinstance(op, ast.GtE):
                    constraints.append(left >= right)
        return And(constraints) if constraints else None
    elif isinstance(node, ast.BoolOp):
        op = node.op
        values = [ast_to_z3_expr(value, variables) for value in node.values]
        if all(value is not None for value in values):
            if isinstance(op, ast.And):
                return And(values)
            elif isinstance(op, ast.Or):
                return Or(values)
    elif isinstance(node, ast.UnaryOp):
        operand = ast_to_z3_expr(node.operand, variables)
        op = node.op
        return Not(operand) if operand is not None and isinstance(op, ast.Not) else None
    return None

def extract_constraints(node, path_constraints, variables):
    if isinstance(node, ast.If):
        condition = node.test
        constraint = ast_to_z3_expr(condition, variables)
        if constraint is not None:
            path_constraints.append(constraint)
        extract_constraints(node.body, path_constraints, variables)
        extract_constraints(node.orelse, path_constraints, variables)

def get_all_path_constraints(program):
    tree = ast.parse(program)
    visiter = ast.NodeVisitor()
    variables = {name.id for name in ast.walk(tree) if isinstance(name, ast.Name)}
    all_path_constraints = []
    for node in ast.walk(tree):
        print(node)
        if isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                if isinstance(stmt, ast.If):
                    print('-------------start-----------')
                    print('-------------dumped_stmt.test-----------')
                    print(ast.dump(stmt.test))
                    print('-------------dumped_stmt.orelse-----------')
                    print(type(stmt.orelse))
                    for n in stmt.orelse:
                        print(ast.dump(n))
                        print(ast.dump(n.test.left))
                        print(ast.parse(n).test.left.id)
                    print('-------------end-----------')
                    path_constraints = []
                    extract_constraints(stmt.test, path_constraints, variables)
                    all_path_constraints.append(path_constraints)

    return all_path_constraints

if __name__ == "__main__":
    #    sample_program = """
    #def example_function(x):
    #    if x > 0 or x < 888 & x > 10 & x < 100:
    #        y = x + 1
    #        if y > 0 & y < 888:
    #            y = x - 1
    #        if y > 10:
    #            y = y + 1
    #    elif x < 0:
    #        y = x - 1
    #    return y
    #"""
    sample_program = """
a = 123
b = a * 10
c = a * b
"""
    all_path_constraints = get_all_path_constraints(sample_program)

    for index, path_constraints in enumerate(all_path_constraints):
        print(f"Path {index + 1} Constraints: {path_constraints}")

