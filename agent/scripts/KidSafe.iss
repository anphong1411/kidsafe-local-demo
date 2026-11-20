#ifndef Payload
  #error Payload directory is required
#endif

[Setup]
AppId=KidSafe.Windows
AppName=KidSafe
AppVersion=1.0.1
AppPublisher=KidSafe
DefaultDirName={autopf}\KidSafe
DisableDirPage=yes
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
MinVersion=10.0.10240
PrivilegesRequired=admin
OutputBaseFilename=KidSafe-Setup-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UsePreviousAppDir=no
CloseApplications=no

[Files]
Source: "{#Payload}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{commonprograms}\KidSafe"; Filename: "{app}\runtime\pythonw.exe"; Parameters: "-I ""{app}\agent\tray.py"" --config ""{commonappdata}\KidSafe\tray\config.json"""; WorkingDir: "{app}"

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if WizardSilent then
    Result := 'Open KidSafe Setup interactively to choose the child account and enter the pairing code.'
  else if CompareText(ExpandConstant('{app}'), ExpandConstant('{autopf}\KidSafe')) <> 0 then
    Result := 'KidSafe must be installed in its protected Program Files folder.'
  else if DirExists(ExpandConstant('{app}')) or DirExists(ExpandConstant('{commonappdata}\KidSafe')) then
    Result := 'An existing KidSafe installation or recovery folder was found. Remove it safely before installing.';
end;

function RunKidSafeScript(ScriptName, Extra: String): Boolean;
var
  ExitCode: Integer;
begin
  Result := Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'),
    '-NoProfile -NonInteractive -STA -ExecutionPolicy Bypass -File "' +
    ExpandConstant('{app}\agent\scripts\') + ScriptName + '" ' + Extra,
    ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ExitCode) and (ExitCode = 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    if not RunKidSafeScript('Pair-WindowsSetup.ps1', '') then
      RaiseException('KidSafe setup did not finish. Review the pairing message before trying again.');
end;

function InitializeUninstall(): Boolean;
begin
  Result := RunKidSafeScript('Uninstall-ChildLab.ps1', '-ChildLab -BundledRuntime');
  if not Result then
    MsgBox('KidSafe could not be removed safely. Its files have been kept for DNS and service recovery.', mbError, MB_OK);
end;
