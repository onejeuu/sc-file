[Setup]
AppId=onejeuu.scfile
AppName=scfile
AppVersion={#AppVersion}
AppPublisher=onejeuu
AppPublisherURL=https://github.com/onejeuu/sc-file
AppSupportURL=https://github.com/onejeuu/sc-file/issues
AppUpdatesURL=https://github.com/onejeuu/sc-file/releases/latest
OutputDir=..\dist
DefaultDirName={localappdata}\Programs\scfile
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputBaseFilename=scfile_setup
SetupIconFile=..\assets\scfile.ico
UninstallDisplayIcon={app}\scfile.exe
UninstallFilesDir={app}\bin\uninstall
SolidCompression=yes
WizardStyle=modern
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\setup\scfile\scfile.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\setup\scfile\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\scfile"; Filename: "{app}\scfile.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\scfile"; Filename: "{app}\scfile.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\scfile.exe"; Description: "{cm:LaunchProgram,scfile}"; Flags: nowait postinstall skipifsilent unchecked
