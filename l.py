import ast


def get_all_path_constraints(program):
    tree = ast.parse(program)
    visiter = ast.NodeVisitor()
    variables = {name.id for name in ast.walk(tree) if isinstance(name, ast.Name)}
    all_path_constraints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for stmt in node.body:
                if isinstance(stmt, ast.If):
                    print('-------------start-----------')
                    print(ast.dump(stmt.test, indent=4))
                    print('-------------end-----------')

if __name__ == "__main__":
    sample_program = """
def example_function(x):
    y = 10
    if 0 > y or x < 888 & x > 10 & x < 100:
        y = x + 1
        if x > 10:
            y = x + 2
    return y
"""
    get_all_path_constraints(sample_program)
    print()
    print(sample_program)
    print()
    sample_program = """
def example_function(x):
    if x > 10 & x < 100 & x > 10:
        y = x + 1
    return y
"""
    get_all_path_constraints(sample_program)
    print()
    print(sample_program)
    print()
