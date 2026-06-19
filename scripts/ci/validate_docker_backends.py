"""Gate CI: valida que build.sh solo construya backends Docker oficiales."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "docker" / "scripts" / "build.sh"
OFFICIAL_BACKENDS = {"python", "javascript", "rust"}
_ALLOWED_IMAGES = {"cobra", *(f"cobra-{backend}" for backend in OFFICIAL_BACKENDS)}
IMAGE_PATTERN = re.compile(r"(?:^|\s)(?:-t\s+)?(cobra(?:-[a-z0-9_-]+)?)(?=\s|$)")
DOCKERFILE_PATTERN = re.compile(r"docker/backends/([a-z0-9_-]+)\.Dockerfile")


def _build_script_tokens() -> tuple[set[str], set[str]]:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    images = set(IMAGE_PATTERN.findall(text))
    dockerfile_backends = set(DOCKERFILE_PATTERN.findall(text))
    return images, dockerfile_backends


def find_violations() -> list[str]:
    images, dockerfile_backends = _build_script_tokens()
    violations: list[str] = []
    forbidden_images = sorted(image for image in images if image not in _ALLOWED_IMAGES)
    if forbidden_images:
        violations.append(
            "imágenes no oficiales en docker/scripts/build.sh: "
            + ", ".join(forbidden_images)
        )

    forbidden_dockerfiles = sorted(
        backend for backend in dockerfile_backends if backend not in OFFICIAL_BACKENDS
    )
    if forbidden_dockerfiles:
        violations.append(
            "Dockerfiles de backend no oficiales referenciados en docker/scripts/build.sh: "
            + ", ".join(f"docker/backends/{backend}.Dockerfile" for backend in forbidden_dockerfiles)
        )
    return violations


def main() -> int:
    violations = find_violations()
    if violations:
        print("❌ Gate de backends Docker oficiales: FALLÓ", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        print(
            "Regla: docker/scripts/build.sh solo puede construir cobra, "
            "cobra-python, cobra-javascript y cobra-rust.",
            file=sys.stderr,
        )
        return 1

    print("✅ Gate de backends Docker oficiales: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
