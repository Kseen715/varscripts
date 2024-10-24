$ErrorActionPreference = "Stop"

$VSCODE_DEV = $null
$ELECTRON_RUN_AS_NODE = 1

$codeInsidersPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\Code - Insiders.exe"
$cliPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\resources\app\out\cli.js"

& $codeInsidersPath --file-uri $cliPath @args

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}