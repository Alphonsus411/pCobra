# -*- coding: utf-8 -*-
"""Transpilador inverso desde Julia a Cobra usando tree-sitter."""

from .tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromJulia(TreeSitterReverseTranspiler):
    LANGUAGE = "julia"
