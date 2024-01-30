import ast

def extract_logical_expression(node):
    if isinstance(node, ast.Compare):
        left = node.left.id
        ops = [op.__class__.__name__ for op in node.ops]
        comparators = [extract_logical_expression(comp) for comp in node.comparators]
        return f"{left} {' '.join(ops)} {' '.join(comparators)}"
    
    elif isinstance(node, ast.BinOp):
        left = extract_logical_expression(node.left)
        op = node.op.__class__.__name__
        right = extract_logical_expression(node.right)
        return f"({left} {op} {right})"
    
    elif isinstance(node, ast.Constant):
        return str(node.value)
    
    elif isinstance(node, ast.Name):
        return node.id
    
    else:
        raise ValueError(f"Unsupported node type: {type(node)}")

ast_node = ast.Compare(
    left=ast.Name(id='x', ctx=ast.Load()),
    ops=[ast.Gt(), ast.Lt(), ast.Gt(), ast.Lt()],
    comparators=[
        ast.BinOp(
            left=ast.Constant(value=0),
            op=ast.BitAnd(),
            right=ast.Name(id='x', ctx=ast.Load())
        ),
        ast.BinOp(
            left=ast.Constant(value=888),
            op=ast.BitAnd(),
            right=ast.Name(id='x', ctx=ast.Load())
        ),
        ast.BinOp(
            left=ast.Constant(value=10),
            op=ast.BitAnd(),
            right=ast.Name(id='x', ctx=ast.Load())
        ),
        ast.Constant(value=100)
    ]
)

logical_expression = extract_logical_expression(ast_node)
print(logical_expression)

