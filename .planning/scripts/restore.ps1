# daip-live 正式恢复脚本（S3-3 交付物，2026-08-09）
# 用途：从备份 zip 恢复 daip_live.db / knowledge/ / config.yaml 到项目根
# 注意：这是破坏性操作——覆盖当前文件。执行前自动备份当前状态。
#
# 用法:
#   pwsh .planning/scripts/restore.ps1 -Zip backups/daip-20260808-082131.zip
#   pwsh .planning/scripts/restore.ps1 -Zip backups/daip-20260808-082131.zip -Yes   # 跳过确认
#
# 背景（见 .planning/real_state_assessment_2026-08-09.md §3.3）：
# 当前 root daip_live.db 被 S2 测试战役污染（64 个 Test session、dialogue_turns 归零），
# 备份中保留 406 会话/611 轮真实数据（演练已验证可读）。

param(
    [Parameter(Mandatory = $true)]
    [string]$Zip,
    [switch]$Yes
)

$ProjectRoot = Split-Path $PSScriptRoot -Parent | Split-Path -Parent
$Zip = Join-Path $ProjectRoot $Zip

if (-not (Test-Path -LiteralPath $Zip)) { throw "备份文件不存在: $Zip" }

# 恢复前自动备份当前状态（防误操作）
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$pre = Join-Path $ProjectRoot "backups\pre-restore-$stamp.zip"
Write-Host "[restore] 恢复前备份当前状态 -> $pre"
Compress-Archive -LiteralPath (Join-Path $ProjectRoot "daip_live.db"), (Join-Path $ProjectRoot "knowledge"), (Join-Path $ProjectRoot "config.yaml") -DestinationPath $pre -CompressionLevel Optimal

if (-not $Yes) {
    Write-Host "[restore] 将解压 $Zip 覆盖项目根的 daip_live.db / knowledge/ / config.yaml"
    $ans = Read-Host "确认执行? (y/N)"
    if ($ans -notin @("y", "Y")) { Write-Host "[restore] 已取消"; exit 1 }
}

# 校验 zip 完整性（先演练式解压到临时目录验证 db 可读）
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("daip_restore_" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null
Expand-Archive -LiteralPath $Zip -DestinationPath $tmp
$dbInZip = Get-ChildItem -Path $tmp -Recurse -Filter "daip_live.db" | Select-Object -First 1
if (-not $dbInZip) { Remove-Item -Recurse -Force $tmp; throw "zip 中未找到 daip_live.db" }
$counts = py -c "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); print({t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['sessions','dialogue_turns','debate_sessions','debate_turns','knowledge_sources']})" $dbInZip.FullName
if ($LASTEXITCODE -ne 0) { Remove-Item -Recurse -Force $tmp; throw "备份 db 不可读" }
Write-Host "[restore] 备份内容校验 OK: $counts"

# 正式覆盖
Copy-Item -LiteralPath (Join-Path $tmp "daip_live.db") -Destination (Join-Path $ProjectRoot "daip_live.db") -Force
Get-ChildItem -LiteralPath (Join-Path $tmp "knowledge") -Recurse | ForEach-Object {
    $rel = $_.FullName.Substring((Join-Path $tmp "knowledge").Length)
    $dest = Join-Path (Join-Path $ProjectRoot "knowledge") $rel.TrimStart("\")
    if ($_.PSIsContainer) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
    else { Copy-Item -LiteralPath $_.FullName -Destination $dest -Force }
}
if (Test-Path -LiteralPath (Join-Path $tmp "config.yaml")) {
    Copy-Item -LiteralPath (Join-Path $tmp "config.yaml") -Destination (Join-Path $ProjectRoot "config.yaml") -Force
}
Remove-Item -Recurse -Force $tmp

Write-Host "[restore] 完成。验证: py -c \"import sqlite3; print(sqlite3.connect('daip_live.db').execute('SELECT COUNT(*) FROM sessions').fetchone())\""
Write-Host "[restore] 恢复前状态备份在: $pre"
