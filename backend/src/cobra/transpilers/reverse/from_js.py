# -*- coding: utf-8 -*-
"""Transpilador inverso desde JavaScript a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromJS(TreeSitterReverseTranspiler):
    LANGUAGE = "javascript"
