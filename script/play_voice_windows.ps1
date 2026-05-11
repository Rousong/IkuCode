param(
    [Parameter(Mandatory = $true)]
    [string]$FileName
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$VoiceDir = Join-Path $ProjectDir "voice"

$VoiceFile = Join-Path $VoiceDir $FileName

if (-not (Test-Path $VoiceFile -PathType Leaf)) {
    throw "Voice file not found: $VoiceFile"
}

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class MciPlayer
{
    [DllImport("winmm.dll", CharSet = CharSet.Auto)]
    public static extern int mciSendString(string command, StringBuilder returnValue, int returnLength, IntPtr winHandle);
}
"@

$Alias = "voice_" + [Guid]::NewGuid().ToString("N")
$OpenCommand = "open `"$VoiceFile`" type mpegvideo alias $Alias"
$PlayCommand = "play $Alias wait"
$CloseCommand = "close $Alias"

$OpenResult = [MciPlayer]::mciSendString($OpenCommand, $null, 0, [IntPtr]::Zero)
if ($OpenResult -ne 0) {
    throw "Failed to open MP3 file: $VoiceFile"
}

try {
    $PlayResult = [MciPlayer]::mciSendString($PlayCommand, $null, 0, [IntPtr]::Zero)
    if ($PlayResult -ne 0) {
        throw "Failed to play MP3 file: $VoiceFile"
    }
}
finally {
    [void][MciPlayer]::mciSendString($CloseCommand, $null, 0, [IntPtr]::Zero)
}
