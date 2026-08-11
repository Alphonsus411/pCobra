import ast

parse_source = ast.parse


def export_ast(source):
    return parse_source(source)
