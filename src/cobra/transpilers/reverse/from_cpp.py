# -*- coding: utf-8 -*-
"""Transpilador inverso desde C++ a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromCPP(TreeSitterReverseTranspiler):
    LANGUAGE = "cpp"
