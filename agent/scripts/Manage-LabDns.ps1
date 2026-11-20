[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Apply', 'Restore')][string]$Action,
    [Parameter(Mandatory)][string]$Snapshot,
    [Parameter(Mandatory)][string]$InterfaceIndices
)
$ErrorActionPreference = 'Stop'
$snapshotPath = [IO.Path]::GetFullPath($Snapshot)
$indices = @($InterfaceIndices.Split(',') | ForEach-Object { [int]$_ })
if ($indices.Count -eq 0 -or @($indices | Where-Object { $_ -le 0 }).Count) { throw 'Explicit positive child-lab adapter indices required.' }

if ($Action -eq 'Apply') {
    if (Test-Path -LiteralPath $snapshotPath) { throw 'Unrestored DNS snapshot exists; restore it first.' }
    $adapters = @($indices | ForEach-Object { Get-NetAdapter -InterfaceIndex $_ -ErrorAction Stop })
    $entries = @()
    foreach ($adapter in $adapters) {
        foreach ($family in @('IPv4', 'IPv6')) {
            $setting = Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -AddressFamily $family
            $registryFamily = if ($family -eq 'IPv4') { 'Tcpip' } else { 'Tcpip6' }
            $registryPath = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\$registryFamily\Parameters\Interfaces\$($adapter.InterfaceGuid.ToString('B'))"
            $nameServer = (Get-ItemProperty -LiteralPath $registryPath -Name NameServer -ErrorAction SilentlyContinue).NameServer
            $entries += [pscustomobject]@{ InterfaceGuid=$adapter.InterfaceGuid.ToString(); InterfaceIndex=$adapter.ifIndex; AddressFamily=$family; Static=(-not [string]::IsNullOrWhiteSpace($nameServer)); Servers=@($setting.ServerAddresses) }
        }
    }
    # Persist before the first mutation so kill/restart can restore safely.
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($snapshotPath)) | Out-Null
    $temporaryPath = $snapshotPath + '.new'
    [IO.File]::WriteAllText($temporaryPath, (@{Version=1; Adapters=$entries} | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporaryPath -Destination $snapshotPath
    try {
        foreach ($entry in $entries) {
            $setting = Get-DnsClientServerAddress -InterfaceIndex $entry.InterfaceIndex -AddressFamily $entry.AddressFamily
            $loopback = if ($entry.AddressFamily -eq 'IPv4') { '127.0.0.1' } else { '::1' }
            $setting | Set-DnsClientServerAddress -ServerAddresses @($loopback) -ErrorAction Stop
        }
        Clear-DnsClientCache
    } catch {
        & $PSCommandPath -Action Restore -Snapshot $snapshotPath -InterfaceIndices $InterfaceIndices
        throw
    }
} elseif (Test-Path -LiteralPath $snapshotPath) {
    $saved = Get-Content -LiteralPath $snapshotPath -Raw | ConvertFrom-Json
    if ($saved.Version -ne 1) { throw 'Unrecognized DNS snapshot.' }
    foreach ($entry in $saved.Adapters) {
        # GUID protects against a recycled interface index targeting another adapter.
        $adapter = Get-NetAdapter | Where-Object { $_.InterfaceGuid.ToString() -eq $entry.InterfaceGuid }
        if (-not $adapter) { throw "Adapter missing: $($entry.InterfaceGuid). Snapshot kept for recovery." }
        $setting = Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -AddressFamily $entry.AddressFamily
        if ($entry.Static -and @($entry.Servers).Count -gt 0) {
            $setting | Set-DnsClientServerAddress -ServerAddresses @($entry.Servers) -ErrorAction Stop
        } else {
            $setting | Set-DnsClientServerAddress -ResetServerAddresses -ErrorAction Stop
        }
    }
    Clear-DnsClientCache
    Remove-Item -LiteralPath $snapshotPath
}
