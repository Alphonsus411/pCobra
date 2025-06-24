import importlib, sys

for pkg in ['cli', 'cobra', 'core', 'ia', 'jupyter_kernel', 'tests']:
    try:
        module = importlib.import_module(pkg)
        sys.modules[__name__ + '.' + pkg] = module
    except Exception:
        pass
