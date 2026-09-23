# Run inside the dedicated Python environment. All arguments go to the public updater.
& python (Join-Path $PSScriptRoot "../../update_aiworkspace.py") @args
exit $LASTEXITCODE
