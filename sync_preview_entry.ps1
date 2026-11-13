$ErrorActionPreference = 'Stop'
$previewDirectory = Join-Path $PSScriptRoot 'unity_enhanced\WindowsPreview_v27'
$previewExecutable = Join-Path $previewDirectory 'BirdsNest.exe'
foreach ($required in @('BirdsNest.exe', 'BirdsNest_Data', 'UnityPlayer.dll')) {
    if (!(Test-Path -LiteralPath (Join-Path $previewDirectory $required))) {
        throw "Preview dependency missing: $required"
    }
}
$shortcutPath = Join-Path $PSScriptRoot '双击观看_赵雷鸟巢（最新版）.lnk'
$shortcutShell = New-Object -ComObject WScript.Shell
$shortcut = $shortcutShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $previewExecutable
$shortcut.WorkingDirectory = $previewDirectory
$shortcut.IconLocation = "$previewExecutable,0"
$shortcut.Description = '双击直接观看最新版鸟巢全场，N 切换日夜，1–9 切换视角。'
$shortcut.WindowStyle = 1
$shortcut.Save()
$savedShortcut = $shortcutShell.CreateShortcut($shortcutPath)
if ($savedShortcut.TargetPath -ne $previewExecutable -or $savedShortcut.WorkingDirectory -ne $previewDirectory) {
    throw 'Preview shortcut verification failed'
}
Write-Output "Preview entry verified: $shortcutPath"
