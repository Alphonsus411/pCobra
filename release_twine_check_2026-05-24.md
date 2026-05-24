# Release traceability - 2026-05-24

## Steps executed
1. Regenerated artifacts in `dist/` with `python -m build`.
2. Validated artifacts with `python -m twine check dist/*`.

## twine check output
```
Checking dist/pcobra-10.1.1-py3-none-any.whl: PASSED
Checking dist/pcobra-10.1.1.tar.gz: PASSED
```

## Result
No metadata or README rendering errors were reported by twine.
