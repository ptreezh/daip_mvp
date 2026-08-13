# daip-live 数据安全基线备份脚本（Stage 0 交付物）
# 用法:
#   pwsh .planning/scripts/backup.ps1                    # 备份 db + knowledge + config 到 backups/
#   pwsh .planning/scripts/backup.ps1 -Restore <zip路径>  # 恢复演练: 解压到临时目录并验证 db 可读
# 恢复正式操作（人为执行）: 解压 zip 到项目根，覆盖 daip_live.db / knowledge/ / config.yaml

param(
    [string]$ProjectRoot = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent),
    [string]$Restore = ""
)

$BackupDir = Join-Path $ProjectRoot "backups"
$ErrorLog = Join-Path $BackupDir "backup-error.log"

# 失败时记录错误日志（计划任务静默失败 3 天无发现，2026-08-13 生产审计修复）
trap {
    $msg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $($_.Exception.Message)"
    Write-Error $msg
    try { Add-Content -LiteralPath $ErrorLog -Value $msg -Encoding utf8 } catch { }
    exit 1
}

function Assert-Item($Path) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "缺少待备份项: $Path" }
}

if ($Restore) {
    Write-Host "[restore-drill] 解压 $Restore 到临时目录并验证..."
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("daip_restore_" + [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    Expand-Archive -LiteralPath $Restore -DestinationPath $tmp
    $db = Get-ChildItem -Path $tmp -Recurse -Filter "daip_live.db" | Select-Object -First 1
    if (-not $db) { throw "恢复演练失败: zip 中未找到 daip_live.db" }
    $env:DAIP_RESTORE_DB = $db.FullName
    $counts = py -c "import sqlite3,os; p=os.environ['DAIP_RESTORE_DB']; c=sqlite3.connect(p); print({t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['sessions','dialogue_turns','debate_sessions','debate_turns','knowledge_sources']})"
    if ($LASTEXITCODE -ne 0) { throw "恢复演练失败: db 不可读" }
    Write-Host "[restore-drill] OK: $counts"
    Remove-Item -Recurse -Force $tmp
    Remove-Item Env:\DAIP_RESTORE_DB
    Write-Host "[restore-drill] 临时目录已清理。正式恢复 = 解压覆盖项目根同名路径。"
    exit 0
}

# 备份模式
Assert-Item (Join-Path $ProjectRoot "daip_live.db")
Assert-Item (Join-Path $ProjectRoot "config.yaml")
$knowledge = Join-Path $ProjectRoot "knowledge"
Assert-Item $knowledge

New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zip = Join-Path $BackupDir "daip-$stamp.zip"

$items = @((Join-Path $ProjectRoot "daip_live.db"), $knowledge, (Join-Path $ProjectRoot "config.yaml"))
Compress-Archive -LiteralPath $items -DestinationPath $zip -CompressionLevel Optimal
if (-not (Test-Path -LiteralPath $zip)) { throw "备份失败: zip 未生成" }

Add-Type -AssemblyName System.IO.Compression.FileSystem
$z = [System.IO.Compression.ZipFile]::OpenRead($zip)
$entries = $z.Entries | ForEach-Object { $_.FullName }
$z.Dispose()

Write-Host "[backup] OK: $zip"
Write-Host "[backup] 条目数: $($entries.Count)"
Write-Host "[backup] 待备份项: db=$(Get-Item -LiteralPath (Join-Path $ProjectRoot 'daip_live.db') | Select-Object -ExpandProperty Length) bytes, knowledge=$(Get-ChildItem -LiteralPath $knowledge -Recurse -File | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum) bytes"
Write-Host "[backup] 下一步: 运行 -Restore <zip> 做恢复演练，然后正式恢复 = 解压覆盖项目根。"
