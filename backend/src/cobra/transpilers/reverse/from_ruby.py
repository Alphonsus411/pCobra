# -*- coding: utf-8 -*-
"""Transpilador inverso desde Ruby a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromRuby(TreeSitterReverseTranspiler):
    LANGUAGE = "ruby"
