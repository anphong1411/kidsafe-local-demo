[CmdletBinding()]
param([string]$Python = 'python', [int]$Port = 8443, [string]$Bind = '127.0.0.1', [string[]]$CertificateHosts = @(), [string]$RuntimeDirectory = '.runtime')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        & $Python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11+ x64, then run again with -Python <path to python.exe>.' }
        & .\.venv\Scripts\python.exe -m pip install -r requirements.lock
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed; check network and retry pip install -r requirements.lock.' }
    }
    $labPath = Join-Path $RuntimeDirectory 'lab.json'
    if (-not (Test-Path -LiteralPath $labPath)) {
        $tlsArgs = @('-m', 'scripts.init_lab', '--root', $RuntimeDirectory)
        foreach ($hostName in $CertificateHosts) { $tlsArgs += @('--host', $hostName) }
        & .\.venv\Scripts\python.exe @tlsArgs
        if ($LASTEXITCODE -ne 0) { throw 'Lab initialization failed.' }
    }
    & .\.venv\Scripts\python.exe -m scripts.seed_lab --config $labPath
    if ($LASTEXITCODE -ne 0) { throw 'Database initialization failed.' }
    $labConfig = Get-Content -Raw -LiteralPath $labPath | ConvertFrom-Json
    foreach ($hostName in $CertificateHosts) {
        if ($hostName -notin ($labConfig.KIDSAFE_ALLOWED_HOSTS -split ',')) {
            throw "Existing profile does not include $hostName. Use a NEW RuntimeDirectory to issue matching certificates; existing secrets are never overwritten."
        }
    }
    Write-Host "KidSafe: https://localhost:$Port/login"
    Write-Host "Tai khoan: $($labConfig.demo_username)"
    Write-Host "Mat khau nam trong file rieng $labPath. Khong chia se file nay."
    Write-Host 'Nhan Ctrl+C de dung. LAN can certificate SAN dung IP/DNS server va CA tren may tre.'
    & .\.venv\Scripts\python.exe -m scripts.run_server --config $labPath --host $Bind --port $Port
} finally { Pop-Location }
