from __future__ import annotations

import hashlib
from pathlib import Path


EXPECTED_SYNTAX_FIXTURES_SHA256 = (
    "f346d7efd9cab701aacb5563bd61fec24b597940a359c018f757ee1b792cb7d1"
)


def test_existing_syntax_fixtures_were_not_modified() -> None:
    fixtures_root = Path(__file__).resolve().parents[1] / "fixtures"
    fixture_files = sorted(fixtures_root.rglob("*.cobra"))

    digest = hashlib.sha256()
    for fixture_file in fixture_files:
        digest.update(fixture_file.relative_to(fixtures_root.parent).as_posix().encode())
        digest.update(b"\0")
        digest.update(fixture_file.read_bytes())
        digest.update(b"\0")

    assert len(fixture_files) == 9
    assert digest.hexdigest() == EXPECTED_SYNTAX_FIXTURES_SHA256
