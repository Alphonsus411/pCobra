# -*- coding: utf-8 -*-
"""Transpilador inverso desde Java a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromJava(TreeSitterReverseTranspiler):
    LANGUAGE = "java"
