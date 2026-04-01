from core.nativos import *
from corelibs import *
from standard_library import *
async def saluda():
    with contextlib.ExitStack() as __cobra_defer_stack_0:
        print(1)
async def principal():
    with contextlib.ExitStack() as __cobra_defer_stack_1:
        await saluda()
await principal()
