import asyncio

import pytest

from pcobra.standard_library import asincrono as std_asincrono


@pytest.mark.asyncio
async def test_limitar_tiempo_disponible_en_standard_library():
    async with std_asincrono.limitar_tiempo(0.05):
        await asyncio.sleep(0)
