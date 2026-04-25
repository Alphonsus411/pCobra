from __future__ import annotations

from scripts.ci.check_core_scc import classify_core_sccs


def test_classifica_scc_inesperada_como_no_permitida() -> None:
    cyclic_components = [
        {"pcobra.core.alpha", "pcobra.core.beta"},
    ]

    allowed, forbidden, unexpected = classify_core_sccs(cyclic_components)

    assert allowed == []
    assert forbidden == []
    assert unexpected == cyclic_components
