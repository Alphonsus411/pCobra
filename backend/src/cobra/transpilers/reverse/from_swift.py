# -*- coding: utf-8 -*-
"""Transpilador inverso desde Swift a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromSwift(TreeSitterReverseTranspiler):
    LANGUAGE = "swift"
