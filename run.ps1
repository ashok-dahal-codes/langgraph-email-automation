param(
    [ValidateSet('check', 'index', 'run', 'api', 'demo')]
    [string]$Mode = 'check'
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Missing .venv. Install Python 3.12, create .venv and install requirements.txt.'
}
$entryPoint = switch ($Mode) {
    'check' { 'check_setup.py' }
    'index' { 'create_index.py' }
    'demo' { 'demo.py' }
    'run' { 'main.py' }
    'api' { 'deploy_api.py' }
}
& $projectPython $entryPoint
exit $LASTEXITCODE

