import ast

parse_source = ast.parse


def validate_ast(tree):
    if not isinstance(tree, ast.AST):
        raise TypeError("expected an AST")


def export_ast(source):
    tree = parse_source(source)
    validate_ast(tree)
    return tree
