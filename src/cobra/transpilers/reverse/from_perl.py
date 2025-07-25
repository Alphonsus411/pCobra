# -*- coding: utf-8 -*-
"""Transpilador inverso desde Perl a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromPerl(TreeSitterReverseTranspiler):
    LANGUAGE = "perl"
