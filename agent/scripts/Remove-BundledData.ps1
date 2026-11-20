# Remove only the known files after the service stops and DNS is restored.
$dataRoot = Join-Path $env:ProgramData 'KidSafe'
foreach ($name in @('service\ca.crt','service\config.json','service\config.new','service\config.backup','service\setup-ready','service\cache.db',
        'service\cache.db-wal','service\cache.db-shm','tray\config.json','service','tray','')) {
    $item = Get-Item -LiteralPath (Join-Path $dataRoot $name) -ErrorAction SilentlyContinue
    if ($item) { $item.Delete() }
}
