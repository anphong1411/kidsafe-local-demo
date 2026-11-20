[CmdletBinding()]
param([string]$InstallDirectory="$env:ProgramFiles\KidSafe", [switch]$ChildLab, [switch]$BundledRuntime)
$ErrorActionPreference = 'Stop'
if (-not $ChildLab) { throw 'Explicit -ChildLab required on the authorized child machine.' }
$installRoot = [IO.Path]::GetFullPath($InstallDirectory)
$programFilesRoot = [IO.Path]::GetFullPath($env:ProgramFiles).TrimEnd('\') + '\'
if (-not $installRoot.StartsWith($programFilesRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected installation target.' }
$configPath = Join-Path $env:ProgramData 'KidSafe\service\config.json'
if ($BundledRuntime -and -not (Test-Path -LiteralPath (Join-Path $env:ProgramData 'KidSafe')) -and
    -not (Get-Service KidSafe -ErrorAction SilentlyContinue)) { return }
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
if ([IO.Path]::GetFullPath($config.tray_script) -ne (Join-Path $installRoot 'agent\tray.py')) { throw 'Configured installation does not match requested directory.' }
foreach ($task in @('KidSafe visible tray','KidSafe service at child logon')) {
    if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $task -Confirm:$false
    }
}
$service = Get-Service KidSafe -ErrorAction SilentlyContinue
if ($service) {
    if ($BundledRuntime) {
        Set-Service KidSafe -StartupType Disabled
        if ($service.Status -ne 'Stopped') { Stop-Service KidSafe }
        $service.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(40))
    } else { Stop-Service KidSafe -Force -ErrorAction SilentlyContinue }
}
& (Join-Path $installRoot 'agent\scripts\Manage-LabDns.ps1') -Action Restore -Snapshot $config.dns_snapshot -InterfaceIndices (@($config.dns_interfaces) -join ',')
if ($config.manage_browser_doh) {
    & (Join-Path $installRoot 'agent\scripts\Manage-LabBrowserPolicy.ps1') -Action Restore -Snapshot $config.browser_policy_snapshot -ChildLab
}
if ($BundledRuntime) {
    if ($service) {
        & sc.exe delete KidSafe | Out-Null
        if ($LASTEXITCODE) { throw 'Service removal failed.' }
    }
    & (Join-Path $PSScriptRoot 'Remove-BundledData.ps1')
    return
}
$agentPython = Join-Path $installRoot '.venv\Scripts\python.exe'
Push-Location -LiteralPath $installRoot
try { & $agentPython -m agent.service remove; if ($LASTEXITCODE) { throw 'Service removal failed.' } } finally { Pop-Location }
# Keep source/environment and protected service metadata for explicit review/recovery.
# No recursive delete is performed by this uninstaller.
Write-Host 'Service/tasks removed and original DNS restored. Protected installation and ProgramData are retained for review. Remove the device in the parent dashboard to revoke server tokens and request cache deletion before uninstalling when possible.'
