# -*- coding: utf-8 -*-
"""Transpilador inverso desde Kotlin a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromKotlin(TreeSitterReverseTranspiler):
    LANGUAGE = "kotlin"
