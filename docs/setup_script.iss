; Script generated for Ravenfoot P100 (Professional Edition)
[Setup]
AppName=Ravenfoot P100
AppVersion=1.2.0
DefaultDirName={autopf}\Ravenfoot P100
DefaultGroupName=Ravenfoot
OutputBaseFilename=Ravenfoot_P100_Installer
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=ravenfoot_icon.ico
UninstallDisplayIcon={app}\Ravenfoot P100.exe

[Files]
; Point strictly to your compiled EXE
Source: "dist\Ravenfoot P100.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Ravenfoot P100"; Filename: "{app}\Ravenfoot P100.exe"
Name: "{autodesktop}\Ravenfoot P100"; Filename: "{app}\Ravenfoot P100.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"