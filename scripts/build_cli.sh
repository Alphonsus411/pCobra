#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"

pip install --no-cache-dir -r requirements.txt

pyinstaller --onefile --clean --strip cobra-cli.spec

HASH1=$(sha256sum dist/cobra-cli | awk '{print $1}')
echo "Primer hash: $HASH1"

rm -rf build dist
pyinstaller --onefile --clean --strip cobra-cli.spec
HASH2=$(sha256sum dist/cobra-cli | awk '{print $1}')
echo "Segundo hash: $HASH2"

if [ "$HASH1" != "$HASH2" ]; then
    echo "Error: los hashes no coinciden"
    exit 1
fi

echo "Hash verificado: $HASH1"
