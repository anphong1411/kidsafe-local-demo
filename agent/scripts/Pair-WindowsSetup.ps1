# Launched from the installed, administrator-owned Program Files directory.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()

$form = [Windows.Forms.Form]::new()
$form.Text = 'Kết nối KidSafe'
$form.Font = [Drawing.Font]::new('Segoe UI', 10)
$form.ClientSize = [Drawing.Size]::new(538, 390)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false

function Add-Label([string]$Text, [int]$Y, [int]$Height = 25) {
    $label = [Windows.Forms.Label]::new()
    $label.Text = $Text
    $label.SetBounds(24, $Y, 490, $Height)
    $form.Controls.Add($label)
}
function Add-Input([Windows.Forms.Control]$Control, [int]$Y, [int]$Width = 490) {
    $Control.SetBounds(24, $Y, $Width, 32)
    $form.Controls.Add($Control)
    return $Control
}

Add-Label 'Chỉ cài trên máy của con. Chuẩn bị tệp kết nối và mã 10 phút từ trang Thiết bị & ghép đôi của phụ huynh.' 18 48
Add-Label 'Tệp kết nối KidSafe' 76
$profileBox = Add-Input ([Windows.Forms.TextBox]::new()) 101 365
$profileBox.ReadOnly = $true
$browse = [Windows.Forms.Button]::new()
$browse.Text = 'Chọn tệp…'
$browse.SetBounds(400, 100, 114, 30)
$form.Controls.Add($browse)
$browse.Add_Click({
    $picker = [Windows.Forms.OpenFileDialog]::new()
    try {
        $picker.Filter = 'Tệp kết nối KidSafe (*.kidsafe)|*.kidsafe'
        $picker.RestoreDirectory = $true
        if ($picker.ShowDialog($form) -eq 'OK') { $profileBox.Text = $picker.FileName }
    } finally { $picker.Dispose() }
})

Add-Label 'Mã ghép đôi (8 ký tự)' 143
$code = Add-Input ([Windows.Forms.TextBox]::new()) 168
$code.MaxLength = 9
$code.CharacterCasing = 'Upper'

Add-Label 'Tài khoản Windows thường của con' 209
$users = Add-Input ([Windows.Forms.ComboBox]::new()) 234
$users.DropDownStyle = 'DropDownList'
$admins = @(Get-LocalGroupMember -SID 'S-1-5-32-544' | ForEach-Object { $_.SID.Value })
foreach ($user in (Get-LocalUser | Where-Object { $_.Enabled -and $_.SID.Value -notin $admins -and $_.SID.Value -notmatch '-50[0-4]$' })) {
    [void]$users.Items.Add($user.Name)
}
if ($users.Items.Count -eq 1) { $users.SelectedIndex = 0 }

Add-Label 'Kết nối mạng để áp dụng lọc web' 270
$adapters = Add-Input ([Windows.Forms.ComboBox]::new()) 295
$adapters.DropDownStyle = 'DropDownList'
$adapters.DisplayMember = 'Name'
foreach ($adapter in (Get-NetAdapter | Where-Object Status -eq 'Up')) {
    [void]$adapters.Items.Add($adapter)
}
if ($adapters.Items.Count -eq 1) { $adapters.SelectedIndex = 0 }

$submit = [Windows.Forms.Button]::new()
$submit.Text = 'Cài và ghép đôi'
$submit.SetBounds(354, 343, 160, 34)
$form.Controls.Add($submit)
$form.AcceptButton = $submit
$submit.Add_Click({
    try {
        if ($users.Items.Count -eq 0) { throw 'Hãy tạo tài khoản Windows loại Standard user cho con trước khi cài.' }
        if (-not $profileBox.Text -or $code.Text -notmatch '^[A-Z2-9]{4}-?[A-Z2-9]{4}$' -or
            $users.SelectedIndex -lt 0 -or $adapters.SelectedIndex -lt 0) {
            throw 'Chọn tệp kết nối, tài khoản con và mạng. Nhập đủ 8 ký tự của mã ghép đôi.'
        }
        if ((Get-Item -LiteralPath $profileBox.Text).Length -gt 16384) { throw 'Tệp kết nối không hợp lệ.' }
        $connection = Get-Content -Raw -LiteralPath $profileBox.Text -Encoding UTF8 | ConvertFrom-Json
        if ($connection.format -ne 'kidsafe-pairing-v1' -or $connection.ca_pem -notmatch '^-----BEGIN CERTIFICATE-----' -or
            $connection.certificate_pin -notmatch '^[a-fA-F0-9]{64}$' -or
            $connection.signing_public_key -notmatch '^[A-Za-z0-9+/]{43}=$') {
            throw 'Hãy dùng tệp kết nối tải từ dashboard KidSafe của gia đình.'
        }
        $form.UseWaitCursor = $true
        $submit.Enabled = $false
        $form.Refresh()
        $root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
        & (Join-Path $PSScriptRoot 'Install-ChildLab.ps1') -ChildLab -BundledRuntime -InstallDirectory $root `
            -Python (Join-Path $root 'runtime\python.exe') -ServerUrl $connection.server_url -CaPem $connection.ca_pem `
            -CertificatePin $connection.certificate_pin -SigningPublicKey $connection.signing_public_key `
            -EnrollmentCode $code.Text -ChildUser "$env:COMPUTERNAME\$($users.SelectedItem)" `
            -InterfaceIndices $adapters.SelectedItem.ifIndex
        [void][Windows.Forms.MessageBox]::Show($form, 'Đã ghép đôi. Đăng nhập tài khoản của con để KidSafe hiện ở khay hệ thống.', 'KidSafe')
        $form.DialogResult = 'OK'
        $form.Close()
    } catch {
        [void][Windows.Forms.MessageBox]::Show($form, $_.Exception.Message, 'KidSafe')
    } finally {
        $form.UseWaitCursor = $false
        $submit.Enabled = $true
    }
})

try { $result = $form.ShowDialog() } finally { $form.Dispose() }
if ($result -ne 'OK') { exit 1 }
