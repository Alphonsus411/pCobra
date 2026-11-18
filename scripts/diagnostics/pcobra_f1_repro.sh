#!/usr/bin/env bash
# pCobra F1 evidence collector. Run in a trusted local checkout; never writes to repository.
set -u
REPO="${1:-.}"
REPO="$(cd "$REPO" && pwd -P)" || exit 2
BASE='68e0465d3793078f2c7763f1e51f7748eb8e9f60'
OUT="${2:-$HOME/pcobra-f1-evidence-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT" || exit 2
OUT="$(cd "$OUT" && pwd -P)"
if [[ "$OUT" == "$REPO" || "$OUT" == "$REPO"/* ]]; then
  printf 'ERROR: output must be outside repository\n' >&2; exit 2
fi
cd "$REPO" || exit 2
printf '%s\n' "baseline=$BASE" "observed_head=$(git rev-parse HEAD 2>/dev/null || echo unknown)" "utc=$(date -u +%FT%TZ)" > "$OUT/metadata.txt"
python --version >> "$OUT/metadata.txt" 2>&1 || true
{ command -v cobra || true; command -v docker || true; command -v node || true; command -v rustc || true; } >> "$OUT/metadata.txt"
if [[ "$(git rev-parse HEAD 2>/dev/null)" != "$BASE" ]]; then
  printf 'BLOCKED: checkout HEAD differs from fixed baseline. No execution performed.\n' | tee "$OUT/STATUS.txt" >&2
  exit 3
fi
if ! command -v cobra >/dev/null 2>&1; then
  printf 'BLOCKED: cobra CLI not available in active environment.\n' | tee "$OUT/STATUS.txt" >&2
  exit 4
fi
export PYTHONDONTWRITEBYTECODE=1
TMP="$(mktemp -d)" || exit 2
trap 'rm -rf "$TMP"' EXIT
# Minimal isolated probes. These do not modify repository files or fixtures.
printf 'imprimir("Hola")\n' > "$TMP/hello.cobra"
printf 'func suma(a, b):\n    retorno a + b\nfin\nimprimir(suma(2, 3))\n' > "$TMP/suma.cobra"
printf 'funcion saludar(nombre):\n    retornar f"Hola, {nombre}"\n' > "$TMP/libro_funcion.cobra"
printf 'func potencia(base, exponente = 2):\n    retorno base ** exponente\nfin\nimprimir(potencia(2))\n' > "$TMP/libro_default.cobra"
printf 'func saludar(nombre):\n    retorno nombre\nfin\nimprimir(saludar("Hola"))\n' > "$TMP/func_canonica.cobra"
# Never relax environment security, skip backends, or override SQLite key requirements.
run_case() {
  local id="$1"; shift
  printf '%s\n' "$*" > "$OUT/$id.command.txt"
  "$@" > "$OUT/$id.stdout.txt" 2> "$OUT/$id.stderr.txt"
  local rc=$?
  printf '%s\n' "$rc" > "$OUT/$id.exitcode.txt"
  printf '%s: exit=%s\n' "$id" "$rc" | tee -a "$OUT/RESULTS.txt"
}
cd "$TMP" || exit 2
run_case R01 cobra run "$TMP/suma.cobra"
run_case R02 cobra test "$TMP/suma.cobra"
run_case R03 cobra run "$TMP/libro_funcion.cobra"
run_case R04 cobra run "$TMP/libro_default.cobra"
run_case R05 cobra run "$TMP/func_canonica.cobra"
run_case R06 python "$REPO/scripts/ci/audit_reglas_libro_programacion.py"
printf 'DONE: raw outputs captured without changing project files. Interpret results before marking any roadmap checkbox.\n' | tee "$OUT/STATUS.txt"
