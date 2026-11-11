$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath $PSScriptRoot).ProviderPath.TrimEnd('\')
$taskBackup = 'D:\赵雷鸟巢_历史预览与备份_20261027'
if (Test-Path -LiteralPath $taskBackup) { throw "Backup destination already exists: $taskBackup" }
if (Get-Process -Name Unity -ErrorAction SilentlyContinue) { throw 'Unity is running; project caches were not touched.' }
New-Item -ItemType Directory -Path $taskBackup | Out-Null
$taskManifest = [System.Collections.Generic.List[object]]::new()
function Assert-WorkspacePath([string]$taskPath) {
    $taskResolved = (Resolve-Path -LiteralPath $taskPath).ProviderPath
    if (-not $taskResolved.StartsWith($taskRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Path outside workspace: $taskResolved" }
    if ((Get-Item -LiteralPath $taskResolved -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing reparse point: $taskResolved" }
    return $taskResolved
}
function Move-VerifiedFile([string]$taskSource, [string]$taskDestination) {
    $taskSource = Assert-WorkspacePath $taskSource
    if (Test-Path -LiteralPath $taskDestination) { throw "Destination exists: $taskDestination" }
    $taskParent = Split-Path -Parent $taskDestination
    if (!(Test-Path -LiteralPath $taskParent)) { New-Item -ItemType Directory -Path $taskParent -Force | Out-Null }
    Copy-Item -LiteralPath $taskSource -Destination $taskDestination
    $taskHash = (Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash
    if ((Get-FileHash -LiteralPath $taskDestination -Algorithm SHA256).Hash -ne $taskHash) { throw "Copy hash mismatch: $taskSource" }
    $taskManifest.Add([pscustomobject]@{Source=$taskSource;Backup=$taskDestination;SHA256=$taskHash})
    Remove-Item -LiteralPath $taskSource -Force
}
$taskPreviewRoot = Join-Path $taskRoot 'unity_enhanced'
foreach ($taskName in @('WindowsPreview','WindowsPreview_v4','WindowsPreview_v5','WindowsPreview_v5_1','WindowsPreview_v6','WindowsPreview_v7')) {
    $taskSourceDir = Join-Path $taskPreviewRoot $taskName
    if (!(Test-Path -LiteralPath $taskSourceDir)) { continue }
    $taskSourceDir = Assert-WorkspacePath $taskSourceDir
    $taskItems = @(Get-ChildItem -LiteralPath $taskSourceDir -Recurse -Force)
    if ($taskItems | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw "Reparse point in $taskSourceDir" }
    foreach ($taskFile in ($taskItems | Where-Object { -not $_.PSIsContainer })) {
        $taskRelative = $taskFile.FullName.Substring($taskSourceDir.Length).TrimStart('\')
        Move-VerifiedFile $taskFile.FullName (Join-Path (Join-Path $taskBackup $taskName) $taskRelative)
    }
    Remove-Item -LiteralPath $taskSourceDir -Recurse -Force
    Write-Output "Archived historical preview: $taskName"
}
foreach ($taskFile in (Get-ChildItem -LiteralPath $taskRoot -File -Filter '*.blend1')) {
    Move-VerifiedFile $taskFile.FullName (Join-Path (Join-Path $taskBackup 'Blender自动备份') $taskFile.Name)
    Write-Output "Archived Blender backup: $($taskFile.Name)"
}
$taskManifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $taskBackup '转移校验清单.json') -Encoding UTF8
foreach ($taskRelative in @('unity_enhanced\UnityProject\Library','unity_delivery\Library','unity_delivery\UnityProject\Library')) {
    $taskPath = Join-Path $taskRoot $taskRelative
    if (Test-Path -LiteralPath $taskPath) {
        $taskPath = Assert-WorkspacePath $taskPath
        if (Get-ChildItem -LiteralPath $taskPath -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw "Reparse point in cache $taskPath" }
        Remove-Item -LiteralPath $taskPath -Recurse -Force
        Write-Output "Removed regenerable Unity cache: $taskRelative"
    }
}
Write-Output "Backup location: $taskBackup"
