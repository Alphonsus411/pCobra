#!/usr/bin/env bash
set -euo pipefail

upgrade_flag=""
if [[ "${1:-}" == "--upgrade" ]]; then
  upgrade_flag="--upgrade"
fi

python -m pip install --quiet pip-tools

pip-compile ${upgrade_flag} --resolver=backtracking --strip-extras \
  --output-file=requirements.txt pyproject.toml
pip-compile ${upgrade_flag} --resolver=backtracking --strip-extras --extra dev --extra docs \
  --output-file=requirements-dev.txt pyproject.toml
pip-compile ${upgrade_flag} --resolver=backtracking --strip-extras --extra docs \
  --output-file=docs/requirements.txt pyproject.toml
