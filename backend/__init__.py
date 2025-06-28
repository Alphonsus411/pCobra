import importlib
import sys
from pathlib import Path

path = Path(__file__).resolve().parent / 'src'
if str(path) not in sys.path:
    sys.path.insert(0, str(path))

src_mod = importlib.import_module('src')
sys.modules[__name__ + '.src'] = src_mod
# Propagar submódulos principales
for sub in ['cli', 'cobra', 'core', 'ia', 'jupyter_kernel', 'tests']:
    name = __name__ + '.src.' + sub
    if 'src.' + sub in sys.modules:
        sys.modules[name] = sys.modules['src.' + sub]
