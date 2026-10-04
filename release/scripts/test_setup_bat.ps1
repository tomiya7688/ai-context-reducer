$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$tempBase = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { [IO.Path]::GetTempPath() }
$tempRoot = Join-Path $tempBase 'setup-bat-e2e'
if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
New-Item -ItemType Directory -Path $tempRoot | Out-Null

function Assert-Equal($actual, $expected, $message) {
    if ($actual -ne $expected) { throw "$message (expected '$expected', got '$actual')" }
}

function Invoke-Setup($setupRoot, $projectRoot, $failCommand = '') {
    $log = Join-Path $tempRoot 'commands.log'
    Remove-Item -LiteralPath $log -Force -ErrorAction SilentlyContinue
    $env:ACR_SETUP_STUB_LOG = $log
    $env:ACR_SETUP_STUB_FAIL = $failCommand
    & $env:ComSpec /d /c "`"$(Join-Path $setupRoot 'setup.bat')`" `"$projectRoot`"" | Out-Null
    $exitCode = $LASTEXITCODE
    $commands = @()
    if (Test-Path -LiteralPath $log) { $commands = @(Get-Content -LiteralPath $log) }
    return @{ ExitCode = $exitCode; Commands = $commands }
}

$nativeRoot = Join-Path $tempRoot 'native-tools'
$nativeStub = Join-Path $tempRoot 'acr-toolbox.exe'
New-Item -ItemType Directory -Force (Join-Path $nativeRoot 'common/native/acr-toolbox/dist') | Out-Null
Copy-Item (Join-Path $repoRoot 'tools/setup.bat') (Join-Path $nativeRoot 'setup.bat')
Push-Location $repoRoot
try {
    & go build -o $nativeStub release/scripts/setup_bat_stub.go
    if ($LASTEXITCODE -ne 0) { throw 'could not build setup.bat native stub' }
} finally { Pop-Location }
Copy-Item $nativeStub (Join-Path $nativeRoot 'common/native/acr-toolbox/dist/acr-toolbox.exe')
$project = Join-Path $tempRoot 'project'
New-Item -ItemType Directory -Force $project | Out-Null

$success = Invoke-Setup $nativeRoot $project
Assert-Equal $success.ExitCode 0 'native success should return zero'
Assert-Equal ($success.Commands -join ',') 'env,language-env,analyze,language-setup,language-run' 'native success should run each step in order'
foreach ($command in @('env', 'language-env', 'analyze', 'language-setup', 'language-run')) {
    $failed = Invoke-Setup $nativeRoot $project $command
    Assert-Equal $failed.ExitCode 23 "native $command failure should propagate"
    Assert-Equal ($failed.Commands -join ',') (($success.Commands | Select-Object -First ([array]::IndexOf($success.Commands, $command) + 1)) -join ',') "native $command failure should stop later steps"
}

$pythonRoot = Join-Path $tempRoot 'python-tools'
New-Item -ItemType Directory -Force $pythonRoot | Out-Null
Copy-Item (Join-Path $repoRoot 'tools/setup.bat') (Join-Path $pythonRoot 'setup.bat')
$shimDir = Join-Path $tempRoot 'shim'
New-Item -ItemType Directory -Force $shimDir | Out-Null
Copy-Item $nativeStub (Join-Path $shimDir 'py.exe')
$originalPath = $env:PATH
try {
    $env:PATH = "$shimDir;$originalPath"
    $env:ACR_SETUP_STUB_PY_FAIL = ''
    $pythonSuccess = Invoke-Setup $pythonRoot $project
    Assert-Equal $pythonSuccess.ExitCode 0 'Python launcher success should return zero'
    Assert-Equal $pythonSuccess.Commands.Count 4 'Python launcher should run all four steps'
    $pythonScripts = @('language_environment_plan.py', 'analyze_and_recommend.py', 'language_setup.py', 'language_run.py')
    for ($index = 0; $index -lt $pythonScripts.Count; $index++) {
        $script = $pythonScripts[$index]
        $env:ACR_SETUP_STUB_PY_FAIL = $script
        $pythonFailure = Invoke-Setup $pythonRoot $project
        Assert-Equal $pythonFailure.ExitCode 24 "Python launcher $script failure should propagate"
        Assert-Equal $pythonFailure.Commands.Count ($index + 1) "Python launcher $script failure should stop later steps"
    }
} finally {
    $env:PATH = $originalPath
    Remove-Item Env:ACR_SETUP_STUB_PY_FAIL -ErrorAction SilentlyContinue
    Remove-Item Env:ACR_SETUP_STUB_LOG -ErrorAction SilentlyContinue
    Remove-Item Env:ACR_SETUP_STUB_FAIL -ErrorAction SilentlyContinue
}

$plainPythonShim = Join-Path $tempRoot 'plain-python-shim'
New-Item -ItemType Directory -Force $plainPythonShim | Out-Null
Copy-Item $nativeStub (Join-Path $plainPythonShim 'python.exe')
Copy-Item $nativeStub (Join-Path $plainPythonShim 'where.exe')
try {
    # The where.exe stub forces setup.bat to skip `py` and select this `python`.
    $env:PATH = "$plainPythonShim;$env:SystemRoot\System32;$env:SystemRoot"
    $env:ACR_SETUP_STUB_PY_FAIL = ''
    $plainSuccess = Invoke-Setup $pythonRoot $project
    Assert-Equal $plainSuccess.ExitCode 0 'plain Python success should return zero'
    Assert-Equal $plainSuccess.Commands.Count 4 'plain Python fallback should run all four steps'
    $pythonScripts = @('language_environment_plan.py', 'analyze_and_recommend.py', 'language_setup.py', 'language_run.py')
    for ($index = 0; $index -lt $pythonScripts.Count; $index++) {
        $script = $pythonScripts[$index]
        $env:ACR_SETUP_STUB_PY_FAIL = $script
        $plainFailure = Invoke-Setup $pythonRoot $project
        Assert-Equal $plainFailure.ExitCode 24 "plain Python $script failure should propagate"
        Assert-Equal $plainFailure.Commands.Count ($index + 1) "plain Python $script failure should stop later steps"
    }
} finally {
    $env:PATH = $originalPath
    Remove-Item Env:ACR_SETUP_STUB_PY_FAIL -ErrorAction SilentlyContinue
    Remove-Item Env:ACR_SETUP_STUB_LOG -ErrorAction SilentlyContinue
    Remove-Item Env:ACR_SETUP_STUB_FAIL -ErrorAction SilentlyContinue
}

Write-Host 'setup.bat success and failure propagation checks passed.'
exit 0
