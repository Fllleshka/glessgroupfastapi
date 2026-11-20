<#
  Обновление GlessGroup API на IIS до указанного коммита.
  Запускается раннером GitHub Actions из deploy.yml, можно и вручную:
    powershell -ExecutionPolicy Bypass -File .\deploy\deploy.ps1 -Commit <sha>

  Шаги:
    1. проверка, что в рабочей копии сервера нет ручных правок;
    2. резервная копия баз SQLite;
    3. переход на коммит, остановка пула, pip install, запуск пула;
    4. проверка /api/v1/health;
    5. при ошибке — откат на прежний коммит.
#>
param(
    [Parameter(Mandatory = $true)][string]$Commit,
    [string]$App = 'E:\glessgroupfastapi',
    [string]$Backups = 'E:\glessgroupfastapi-backups',
    [string]$Pool = 'glessapi',
    [string]$HostName = 'apigless.gless.group',
    [int]$KeepBackups = 20
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Import-Module WebAdministration

$Python = Join-Path $App '.venv\Scripts\python.exe'

function Step($text) { Write-Host "==> $text" }

function Invoke-Git {
    & git.exe -C $App @args
    if ($LASTEXITCODE -ne 0) { throw "git $args завершился с кодом $LASTEXITCODE" }
}

function Stop-Pool {
    if ((Get-WebAppPoolState -Name $Pool).Value -ne 'Stopped') {
        Stop-WebAppPool -Name $Pool
        for ($i = 0; $i -lt 30 -and (Get-WebAppPoolState -Name $Pool).Value -ne 'Stopped'; $i++) { Start-Sleep 1 }
    }
}

function Install-AndStart {
    Stop-Pool
    & $Python -m pip install --disable-pip-version-check -q -r (Join-Path $App 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'pip install не удался' }
    Start-WebAppPool -Name $Pool
}

# Запрос к своему сайту по HTTPS через 127.0.0.1 — с правильным SNI
function Test-Healthy {
    for ($i = 1; $i -le 10; $i++) {
        Start-Sleep 3
        $out = & curl.exe -fsS --max-time 15 --resolve "${HostName}:443:127.0.0.1" "https://$HostName/api/v1/health"
        if ($LASTEXITCODE -eq 0 -and ($out | Out-String) -match '"status":\s*"ok"') { return $true }
        Write-Host "   попытка $i — сервис пока не отвечает"
    }
    return $false
}

# 1. Рабочая копия чистая
Step "Проверка рабочей копии $App"
$dirty = Invoke-Git status --porcelain --untracked-files=no
if ($dirty) { throw "В $App есть незакоммиченные правки, деплой остановлен:`n$dirty" }
$Previous = (Invoke-Git rev-parse HEAD).Trim()
Write-Host "   сейчас: $Previous"

# 2. Резервная копия баз (sqlite3.backup — корректно и при работающем сервере)
$Data = Join-Path $App 'databasedata'
if (Test-Path $Data) {
    $Backup = Join-Path $Backups ("{0}-{1}" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $Commit.Substring(0, 7))
    Step "Резервная копия баз → $Backup"
    New-Item -ItemType Directory -Force -Path $Backup | Out-Null
    Get-ChildItem $Data -Filter '*.sqlite3' | ForEach-Object {
        & $Python -c "import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close(); s.close()" $_.FullName (Join-Path $Backup $_.Name)
        if ($LASTEXITCODE -ne 0) { throw "Не удалось скопировать $($_.Name)" }
        Write-Host "   $($_.Name)"
    }
    Get-ChildItem $Backups -Directory | Sort-Object Name -Descending |
        Select-Object -Skip $KeepBackups | Remove-Item -Recurse -Force
}

# 3. Новая версия
Step "Переход на $Commit"
Invoke-Git fetch -q --prune origin
Invoke-Git checkout -q --force --detach $Commit
Install-AndStart

# 4. Проверка
Step 'Проверка /api/v1/health'
if (Test-Healthy) {
    Step "Готово: GlessGroup API работает на $Commit"
    exit 0
}

# 5. Откат
Write-Host "::error::Новая версия не прошла проверку — откат на $Previous"
Invoke-Git checkout -q --force --detach $Previous
Install-AndStart
if (Test-Healthy) { Write-Host '   откат выполнен, старая версия отвечает' }
else { Write-Host '::error::Сервис не отвечает и после отката' }
exit 1