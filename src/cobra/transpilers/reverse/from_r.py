# -*- coding: utf-8 -*-
"""Transpilador inverso desde R a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromR(TreeSitterReverseTranspiler):
    LANGUAGE = "r"
