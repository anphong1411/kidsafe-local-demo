[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Apply','Restore')][string]$Action,
    [Parameter(Mandatory)][string]$Snapshot,
    [switch]$ChildLab
)
$ErrorActionPreference = 'Stop'
if (-not $ChildLab) { throw 'Explicit -ChildLab required; never apply to the working host.' }
$snapshotPath = [IO.Path]::GetFullPath($Snapshot)
$policies = @(
    @{Path='SOFTWARE\Policies\Google\Chrome'; Name='DnsOverHttpsMode'; Kind='String'; Value='off'},
    @{Path='SOFTWARE\Policies\Microsoft\Edge'; Name='DnsOverHttpsMode'; Kind='String'; Value='off'},
    @{Path='SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS'; Name='Enabled'; Kind='DWord'; Value=0},
    @{Path='SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS'; Name='Locked'; Kind='DWord'; Value=1}
)
$hive = [Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::LocalMachine, [Microsoft.Win32.RegistryView]::Registry64)
try {
    if ($Action -eq 'Apply') {
        if (Test-Path -LiteralPath $snapshotPath) { throw 'Unrestored browser-policy snapshot exists.' }
        $saved = @()
        foreach ($policy in $policies) {
            $key = $hive.OpenSubKey($policy.Path, $false)
            try {
                $exists = $null -ne $key -and @($key.GetValueNames()) -contains $policy.Name
                $saved += [pscustomobject]@{Path=$policy.Path;Name=$policy.Name;Exists=$exists;Kind=$(if($exists){$key.GetValueKind($policy.Name).ToString()}else{$null});Value=$(if($exists){$key.GetValue($policy.Name,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)}else{$null})}
            } finally { if ($key) { $key.Dispose() } }
        }
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($snapshotPath)) | Out-Null
        [IO.File]::WriteAllText($snapshotPath + '.new', (@{Version=1;Values=$saved} | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
        Move-Item -LiteralPath ($snapshotPath + '.new') -Destination $snapshotPath
        try {
            foreach ($policy in $policies) {
                $key = $hive.CreateSubKey($policy.Path, $true)
                try { $key.SetValue($policy.Name, $policy.Value, [Microsoft.Win32.RegistryValueKind]::$($policy.Kind)) } finally { $key.Dispose() }
            }
        } catch {
            & $PSCommandPath -Action Restore -Snapshot $snapshotPath -ChildLab
            throw
        }
    } elseif (Test-Path -LiteralPath $snapshotPath) {
        $saved = Get-Content -LiteralPath $snapshotPath -Raw | ConvertFrom-Json
        if ($saved.Version -ne 1) { throw 'Unrecognized policy snapshot.' }
        foreach ($value in $saved.Values) {
            if (-not @($policies | Where-Object { $_.Path -eq $value.Path -and $_.Name -eq $value.Name }).Count) { throw 'Unexpected registry target in policy snapshot.' }
            $key = $hive.CreateSubKey($value.Path, $true)
            try {
                if ($value.Exists) {
                    $kind = [Microsoft.Win32.RegistryValueKind]::$($value.Kind)
                    $data = $value.Value
                    if ($kind -eq [Microsoft.Win32.RegistryValueKind]::Binary) { $data = [byte[]]$data }
                    elseif ($kind -eq [Microsoft.Win32.RegistryValueKind]::MultiString) { $data = [string[]]$data }
                    elseif ($kind -eq [Microsoft.Win32.RegistryValueKind]::DWord) { $data = [int]$data }
                    elseif ($kind -eq [Microsoft.Win32.RegistryValueKind]::QWord) { $data = [long]$data }
                    $key.SetValue($value.Name,$data,$kind)
                } else { $key.DeleteValue($value.Name,$false) }
            } finally { $key.Dispose() }
        }
        Remove-Item -LiteralPath $snapshotPath
    }
} finally { $hive.Dispose() }
