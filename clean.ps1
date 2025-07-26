Write-Host "🧹 Limpiando entorno del proyecto..."

Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter *.egg-info | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Proyecto limpio y listo para compilar."

# Limpia carpeta ofuscada (si existe)
Remove-Item -Recurse -Force src\obf_agix -ErrorAction SilentlyContinue

