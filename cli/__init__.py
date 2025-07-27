import importlib
import sys

module = importlib.import_module("cobra.cli")
sys.modules[__name__] = module
