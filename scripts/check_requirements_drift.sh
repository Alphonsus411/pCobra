#!/usr/bin/env bash
set -euo pipefail

./scripts/sync_requirements.sh

git diff --exit-code -- requirements.txt requirements-dev.txt docs/requirements.txt
