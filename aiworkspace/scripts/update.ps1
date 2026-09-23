# Activate the dedicated Python virtual environment first.
& python (Join-Path $PSScriptRoot 'update.py') @args
exit $LASTEXITCODE
