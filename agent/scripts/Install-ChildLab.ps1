[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Python,
    [Parameter(Mandatory)][string]$ServerUrl,
    [string]$CaFile,
    [string]$CaPem,
    [Parameter(Mandatory)][ValidatePattern('^[a-fA-F0-9]{64}$')][string]$CertificatePin,
    [Parameter(Mandatory)][string]$SigningPublicKey,
    [Parameter(Mandatory)][ValidatePattern('^[A-Z2-9]{4}-?[A-Z2-9]{4}$')][string]$EnrollmentCode,
    [Parameter(Mandatory)][string]$ChildUser,
    [Parameter(Mandatory)][int[]]$InterfaceIndices,
    [string]$InstallDirectory = "$env:ProgramFiles\KidSafe",
    [switch]$ChildLab,
    [switch]$BundledRuntime,
    [switch]$DisableBrowserDoh
)
$ErrorActionPreference = 'Stop'
if (-not $ChildLab) { throw 'Specify -ChildLab only on the dedicated authorized child test machine.' }
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Run installation as Administrator on the child lab.' }
$pythonPath = (Resolve-Path -LiteralPath $Python).Path
$installRoot = [IO.Path]::GetFullPath($InstallDirectory)
$programFilesRoot = [IO.Path]::GetFullPath($env:ProgramFiles).TrimEnd('\') + '\'
if (-not $installRoot.StartsWith($programFilesRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Install directory must be under protected Program Files.' }
if (-not $pythonPath.StartsWith($programFilesRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Use a machine-wide Python under Program Files, protected from child writes.' }
if ($BundledRuntime -and ($pythonPath -ne (Join-Path $installRoot 'runtime\python.exe') -or
    $PSScriptRoot -ne (Join-Path $installRoot 'agent\scripts'))) { throw 'Invalid bundled runtime location.' }
if (($BundledRuntime -and -not $CaPem) -or (-not $BundledRuntime -and -not $CaFile)) { throw 'KidSafe CA certificate is required.' }
$childAccount = [Security.Principal.NTAccount]::new($ChildUser)
$childSid = $childAccount.Translate([Security.Principal.SecurityIdentifier])
$resolvedChildUser = $childSid.Translate([Security.Principal.NTAccount]).Value
$admins = Get-LocalGroupMember -SID 'S-1-5-32-544'
if (@($admins | Where-Object { $_.SID -eq $childSid }).Count) { throw 'Child account must be a standard user, not Administrators.' }
if (Get-Service -Name KidSafe -ErrorAction SilentlyContinue) { throw 'KidSafe already installed. Uninstall safely before reinstalling.' }
if (-not $BundledRuntime -and (Test-Path -LiteralPath $installRoot)) { throw 'Install destination already exists; choose a new protected directory.' }
foreach ($task in @('KidSafe visible tray','KidSafe service at child logon')) {
    if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) { throw 'Existing KidSafe scheduled task requires recovery first.' }
}
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$dataRoot = Join-Path $env:ProgramData 'KidSafe'
$serviceRoot = Join-Path $dataRoot 'service'
$trayRoot = Join-Path $dataRoot 'tray'
if (Test-Path -LiteralPath $dataRoot) { throw 'Existing KidSafe ProgramData requires explicit recovery/uninstall first.' }

function Protect-Directory([string]$Path, [bool]$AllowChildRead) {
    $acl = [Security.AccessControl.DirectorySecurity]::new()
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($sid in @([Security.Principal.SecurityIdentifier]::new('S-1-5-18'), [Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))) {
        $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'))
    }
    if ($AllowChildRead) { $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($childSid, 'ReadAndExecute', 'ContainerInherit,ObjectInherit', 'None', 'Allow')) }
    Set-Acl -LiteralPath $Path -AclObject $acl
}

$createdData = $false
$registeredService = $false
$registeredTasks = @()
try {
    if (-not $BundledRuntime) { New-Item -ItemType Directory -Path $installRoot | Out-Null }
    Protect-Directory $installRoot $true
    New-Item -ItemType Directory -Path $dataRoot | Out-Null
    $createdData = $true
    Protect-Directory $dataRoot $true
    New-Item -ItemType Directory -Path $serviceRoot,$trayRoot | Out-Null
    Protect-Directory $serviceRoot $false
    Protect-Directory $trayRoot $true
    if ($BundledRuntime) {
        $agentPython = $pythonPath
        $trayPython = Join-Path $installRoot 'runtime\pythonw.exe'
        $trayBasePython = $trayPython
        [IO.File]::WriteAllText((Join-Path $serviceRoot 'ca.crt'), $CaPem, [Text.Encoding]::ASCII)
        try {
            & $agentPython -I -c "import sys; from agent.transport import PinnedHTTPS; assert PinnedHTTPS(*sys.argv[1:]).request('GET', '/health').get('product') == 'KidSafe'" $ServerUrl (Join-Path $serviceRoot 'ca.crt') $CertificatePin 2>$null
            if ($LASTEXITCODE) { throw 'KidSafe health check failed.' }
        } catch {
            throw 'Không kết nối được máy chủ KidSafe. Hãy kiểm tra mạng LAN và tải lại tệp kết nối từ dashboard.'
        }
    } else {
        Copy-Item -LiteralPath (Join-Path $sourceRoot 'agent') -Destination $installRoot -Recurse
        Copy-Item -LiteralPath (Join-Path $sourceRoot 'requirements.lock') -Destination (Join-Path $installRoot 'requirements.lock')
        & $pythonPath -m venv (Join-Path $installRoot '.venv')
        if ($LASTEXITCODE) { throw 'Failed to create protected agent environment.' }
        $agentPython = Join-Path $installRoot '.venv\Scripts\python.exe'
        $trayPython = Join-Path $installRoot '.venv\Scripts\pythonw.exe'
        $trayBasePython = Join-Path (Split-Path -Parent $pythonPath) 'pythonw.exe'
        if (-not (Test-Path -LiteralPath $trayPython) -or -not (Test-Path -LiteralPath $trayBasePython)) { throw 'Protected Python GUI executables are required for the visible tray.' }
        & $agentPython -m pip install --requirement (Join-Path $installRoot 'requirements.lock')
        if ($LASTEXITCODE) { throw 'Dependency installation failed; no DNS changes have occurred.' }
        Copy-Item -LiteralPath $CaFile -Destination (Join-Path $serviceRoot 'ca.crt')
    }
    $random = [Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] 32
    $random.GetBytes($bytes)
    $ipcToken = [Convert]::ToBase64String($bytes)
    $random.GetBytes($bytes)
    $fingerprint = [Convert]::ToBase64String($bytes)
    $trayConfig = Join-Path $trayRoot 'config.json'
    @{lab_enforcement=$true;ipc_token=$ipcToken;ipc_port=17843} | ConvertTo-Json | Set-Content -LiteralPath $trayConfig -Encoding UTF8
    $config = @{
        lab_enforcement=$true; server_url=$ServerUrl; ca_file=(Join-Path $serviceRoot 'ca.crt'); certificate_pin=$CertificatePin;
        signing_public_key=$SigningPublicKey; database=(Join-Path $serviceRoot 'cache.db'); enrollment_code=$EnrollmentCode.Replace('-', '').ToUpperInvariant();
        fingerprint=$fingerprint; device_name=$env:COMPUTERNAME; upstream=@('1.1.1.1',53); ipc_port=17843; ipc_token=$ipcToken;
        tray_python=$trayPython; tray_base_python=$trayBasePython; tray_script=(Join-Path $installRoot 'agent\tray.py'); tray_config=$trayConfig;
        child_username=$resolvedChildUser; manage_dns=$true; dns_snapshot=(Join-Path $serviceRoot 'dns-before.json'); dns_interfaces=$InterfaceIndices
        block_doh=$DisableBrowserDoh.IsPresent; manage_browser_doh=$DisableBrowserDoh.IsPresent; browser_policy_snapshot=(Join-Path $serviceRoot 'browser-policy-before.json')
    }
    $configPath = Join-Path $serviceRoot 'config.json'
    if ($BundledRuntime) { $config.setup_pending = $true }
    $config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $configPath -Encoding UTF8
    if ($BundledRuntime) {
        $image = '"' + $agentPython + '" -I -m agent.service --run-service'
        New-Service -Name KidSafe -BinaryPathName $image -DisplayName 'KidSafe' -StartupType Automatic | Out-Null
    } else {
        Push-Location -LiteralPath $installRoot
        try {
            & $agentPython -m agent.service --startup auto install
            if ($LASTEXITCODE) { throw 'Service installation failed.' }
        } finally { Pop-Location }
    }
    $registeredService = $true
    & sc.exe failure KidSafe reset= 86400 actions= restart/5000/restart/15000/restart/60000
    if ($LASTEXITCODE) { throw 'SCM recovery configuration failed.' }
    & sc.exe failureflag KidSafe 1
    if ($LASTEXITCODE) { throw 'SCM recovery flag configuration failed.' }
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $resolvedChildUser
    $trayAction = New-ScheduledTaskAction -Execute $trayPython -Argument ('-I "' + $config.tray_script + '" --config "' + $trayConfig + '"') -WorkingDirectory $installRoot
    $trayPrincipal = New-ScheduledTaskPrincipal -UserId $resolvedChildUser -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName 'KidSafe visible tray' -Action $trayAction -Trigger $trigger -Principal $trayPrincipal -Settings $settings | Out-Null
    $registeredTasks += 'KidSafe visible tray'
    $startAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -NonInteractive -WindowStyle Hidden -Command "Start-Service -Name KidSafe"'
    $systemPrincipal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName 'KidSafe service at child logon' -Action $startAction -Trigger $trigger -Principal $systemPrincipal -Settings $settings | Out-Null
    $registeredTasks += 'KidSafe service at child logon'
    if ($BundledRuntime) {
        $readyPath = Join-Path $serviceRoot 'setup-ready'
        & sc.exe start KidSafe | Out-Null
        if ($LASTEXITCODE -and -not (Test-Path -LiteralPath $readyPath)) {
            throw 'Không khởi động được dịch vụ KidSafe để ghép đôi.'
        }
        $deadline = [DateTime]::UtcNow.AddSeconds(45)
        while (-not (Test-Path -LiteralPath $readyPath) -and (Get-Service KidSafe).Status -ne 'Stopped' -and [DateTime]::UtcNow -lt $deadline) {
            Start-Sleep -Milliseconds 400
        }
        if (-not (Test-Path -LiteralPath $readyPath)) {
            throw 'Ghép đôi chưa hoàn tất. Kiểm tra kết nối và tạo mã mới nếu mã đã hết hạn.'
        }
        (Get-Service KidSafe).WaitForStatus('Stopped', [TimeSpan]::FromSeconds(15))
        $paired = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
        $paired.PSObject.Properties.Remove('setup_pending')
        $nextConfig = Join-Path $serviceRoot 'config.new'
        $previousConfig = Join-Path $serviceRoot 'config.backup'
        $paired | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $nextConfig -Encoding UTF8
        [IO.File]::Replace($nextConfig, $configPath, $previousConfig)
        Remove-Item -LiteralPath $readyPath,$previousConfig
    }
    Write-Host 'Installed for the child lab. Sign into the standard child account to start the visible tray and service. DNS changes occur only after a verified visible tray lease; original settings are restored when enforcement stops.'
} catch {
    if ($BundledRuntime -and $createdData) {
        foreach ($task in $registeredTasks) {
            Stop-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $task -Confirm:$false
        }
        if ($registeredService) {
            $service = Get-Service KidSafe
            Set-Service KidSafe -StartupType Disabled
            if ($service.Status -ne 'Stopped') { Stop-Service KidSafe }
            $service.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(40))
            & (Join-Path $PSScriptRoot 'Manage-LabDns.ps1') -Action Restore -Snapshot $config.dns_snapshot -InterfaceIndices ($InterfaceIndices -join ',')
            & sc.exe delete KidSafe | Out-Null
            if ($LASTEXITCODE) { throw 'Không thể dọn dịch vụ KidSafe. Cần kiểm tra trước khi cài lại.' }
        }
        & (Join-Path $PSScriptRoot 'Remove-BundledData.ps1')
    }
    throw
}
