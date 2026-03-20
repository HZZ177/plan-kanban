$Root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $Root "frontend")
pnpm dev
